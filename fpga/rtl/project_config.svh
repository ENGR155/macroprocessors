// EXAMPLE limits. Keep 0 until docs/bringup.md power-stage checks pass.
`define LEV_COMMISSIONED 0
`define LEV_MAX_CURRENT_COUNTS 1241
// Q8.8 gains: Kp 0..4096, Ki 0..1024 including 200 us. Tune before commissioning.
`define LEV_CURRENT_KP_Q8 0
`define LEV_CURRENT_KI_Q8 0
