module pid_controller #(
    parameter logic signed [15:0] KP = 68,
    parameter logic signed [15:0] KI = 1,
    parameter logic signed [15:0] KD = 16222,

    // Integral limit in internal units, before division by 64.
parameter logic signed [31:0] I_LIMIT = 32'sh7FFF_FFFF) (
    input  logic        clk,
    input  logic        n_reset,
    input  logic [15:0] desired_state,
    input  logic [15:0] current_state,
    input  logic        controller_tick,
    output logic [7:0]  out
    // output wire  [15:0] debug_out
);

    // Clamp signed 17-bit arithmetic to a signed 16-bit DSP operand.
    function automatic logic signed [15:0] sat16(
        input logic signed [16:0] x
    );
        if (x[16] == x[15])
            sat16 = x[15:0];
        else
            sat16 = x[16] ? 16'sh8000 : 16'sh7FFF;
    endfunction

    localparam logic signed [32:0] I_MAX =
        {I_LIMIT[31], I_LIMIT};
    localparam logic signed [32:0] I_MIN = -I_MAX;

    logic sample_ready;
    logic [3:0] sample_valid;

    logic signed [16:0] raw_error;
    logic signed [15:0] bounded_error;
    logic signed [15:0] previous_error;
    logic signed [16:0] raw_delta;
    logic have_previous;

    // Align the P/I error with the registered derivative operand.
    logic signed [15:0] error_delay;
    logic signed [15:0] mult_error;
    logic signed [15:0] mult_delta;

    // assign debug_out = mult_delta;

    // ADC updates its output on controller_tick.
    // Wait one clock before sampling that measurement.
    always_ff @(posedge clk) begin
        if (!n_reset) begin
            sample_ready  <= 1'b0;
            sample_valid  <= '0;
            raw_error     <= '0;
            bounded_error <= '0;
            previous_error <= '0;
            raw_delta     <= '0;
            have_previous <= 1'b0;
            error_delay   <= '0;
            mult_error    <= '0;
            mult_delta    <= '0;
        end else begin
            sample_ready <= controller_tick;
            sample_valid <= {sample_valid[2:0], sample_ready};

            // Stage 1: position subtraction only.
            if (sample_ready) begin
                raw_error <=
                    $signed({1'b0, current_state}) -
                    $signed({1'b0, desired_state});
            end

            // Stage 2: error clamp only.
            if (sample_valid[0])
                bounded_error <= sat16(raw_error);

            // Stage 3: derivative subtraction only.
            if (sample_valid[1]) begin
                if (have_previous) begin
                    raw_delta <=
                        $signed({bounded_error[15], bounded_error}) -
                        $signed({previous_error[15], previous_error});
                end else begin
                    raw_delta <= '0;
                end

                previous_error <= bounded_error;
                error_delay    <= bounded_error;
                have_previous  <= 1'b1;
            end

            // Stage 4: derivative clamp and operand alignment.
            if (sample_valid[2]) begin
                mult_delta <= sat16(raw_delta);
                mult_error <= error_delay;
            end
        end
    end

    wire signed [31:0] p_product;
    wire signed [31:0] i_product;
    wire signed [31:0] d_product;

    dsp_mac #(
        .ACCUMULATE_ENABLE(1'b0),
        .SIGNED_ENABLE(1'b1)
    ) proportional (
        .clk(clk),
        .n_reset(n_reset),
        .enable(1'b1),
        .in_a(KP),
        .in_b(mult_error),
        .out(p_product)
    );

    dsp_mac #(
        .ACCUMULATE_ENABLE(1'b0),
        .SIGNED_ENABLE(1'b1)
    ) integral_multiplier (
        .clk(clk),
        .n_reset(n_reset),
        .enable(1'b1),
        .in_a(KI),
        .in_b(mult_error),
        .out(i_product)
    );

    dsp_mac #(
        .ACCUMULATE_ENABLE(1'b0),
        .SIGNED_ENABLE(1'b1)
    ) derivative (
        .clk(clk),
        .n_reset(n_reset),
        .enable(1'b1),
        .in_a(KD),
        .in_b(mult_delta),
        .out(d_product)
    );

    // sample_valid[3] is high when the DSP captures the operands.
    // Three stages later, external registers capture the products.
    logic [2:0] mult_valid;
    logic products_valid;
    logic candidate_valid;
    logic bounded_valid;
    logic total_valid;

    logic signed [31:0] p_reg, i_reg, d_reg;
    logic signed [31:0] i_state;
    logic signed [32:0] i_candidate;
    logic signed [31:0] i_bounded;

    logic signed [32:0] pd_reg;
    logic signed [32:0] pd_delay;
    logic signed [33:0] total_reg;

    always_ff @(posedge clk) begin
        if (!n_reset) begin
            mult_valid     <= '0;
            products_valid <= 1'b0;
            candidate_valid <= 1'b0;
            bounded_valid  <= 1'b0;
            total_valid    <= 1'b0;

            p_reg       <= '0;
            i_reg       <= '0;
            d_reg       <= '0;
            i_state     <= '0;
            i_candidate <= '0;
            i_bounded   <= '0;
            pd_reg      <= '0;
            pd_delay    <= '0;
            total_reg   <= '0;
            out         <= '0;
        end else begin
            mult_valid <= {mult_valid[1:0], sample_valid[3]};

            products_valid  <= mult_valid[2];
            candidate_valid <= products_valid;
            bounded_valid   <= candidate_valid;
            total_valid     <= bounded_valid;

            // Capture aligned full-width DSP products.
            if (mult_valid[2]) begin
                p_reg <= p_product;
                i_reg <= i_product;
                d_reg <= d_product;
            end

            // Separate, parallel additions.
            if (products_valid) begin
                i_candidate <=
                    $signed({i_state[31], i_state}) +
                    $signed({i_reg[31], i_reg});

                pd_reg <=
                    $signed({p_reg[31], p_reg}) +
                    $signed({d_reg[31], d_reg});
            end

            // Integral clamp has its own stage.
            if (candidate_valid) begin
                if (i_candidate > I_MAX) begin
                    i_bounded <= I_LIMIT;
                    i_state   <= I_LIMIT;
                end else if (i_candidate < I_MIN) begin
                    i_bounded <= -I_LIMIT;
                    i_state   <= -I_LIMIT;
                end else begin
                    i_bounded <= i_candidate[31:0];
                    i_state   <= i_candidate[31:0];
                end

                pd_delay <= pd_reg;
            end

            // Final addition has its own stage.
          if (bounded_valid) begin
              total_reg <=
                  $signed({pd_delay[32], pd_delay}) +
($signed({{18{i_bounded[31]}}, i_bounded[31:16]}));
          end

            // Output clamp has its own stage.
          if (total_valid) begin
    if (total_reg < 34'sd0)
        out <= 8'd0;
if (total_reg < 34'sd0)
    out <= 8'd0;
else if (total_reg >= 34'sd32640)
    out <= 8'd255;
else
    out <= total_reg[14:7];
end
        end
    end

endmodule