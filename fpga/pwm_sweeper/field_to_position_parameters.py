import numpy as np
from scipy.optimize import curve_fit
# Define the target file path
desired_resolution_mm = 0.1
position_range_mm=[30, 80]
position_exp = -0.213
position_mm_coefficient = 165
field_range =[]
for bound in position_range_mm:
    field_range += [(int)((bound/position_mm_coefficient)**(1/position_exp))]
field_range_scalar = (int)((field_range[0]-field_range[1])/256)
print(f"Field range scalar: {field_range_scalar}={hex(field_range_scalar)}, Field offset: {field_range[1]}={hex(field_range[1])}")


# Define your target function segment
def target_func(x):
    return position_mm_coefficient*x ** (position_exp)

# Define the reciprocal model you want to fit
def reciprocal_model(x, a, b, c):
    return a + (b / (x+c))

# Choose a local segment (e.g., x from 100 to 500)
x_seg = np.linspace(field_range[1], field_range[0], 100)
y_seg = target_func(x_seg)

# Fit the model to this segment
popt, _ = curve_fit(reciprocal_model, x_seg, y_seg)
a_opt, b_opt, c_opt = popt

print(f"Fitted Segment: y = {a_opt:.4f} + ({b_opt:.4f} / (x + {c_opt:.4f}))")
# shifts = (int)(16-np.ceil(np.log2(b_opt+1)))
scalar = b_opt/(2**13)/desired_resolution_mm
print(f"Scalar: {scalar}, uint equation: y = {(int)(a_opt*scalar)} + ({(int)(b_opt*scalar)} / (x + {(int)(c_opt)}))")
