import math
import numpy as np
import pandas as pd

# Tips_5 = -0.0003
# Tips_7 = 0.0024
# Tips_10 = 0.0035
# Tips_20 = 0.0069
# Tips_30 = 0.0072

# calculation inputs


# user inputs
current_age = 65
sex = 'Male'
inflation_saving = 0
end_draw = 95
percentage_on_survival = 0.5
draw = 50000
inflation_savings = 0
investment = 2200000

# RA inputs
worst_case_inflation = 0.03
future_TIPS_Spread = 0
standard_deviation = 0.0961

average_return = 0.04
annuity_investment_return = 0.025  # 2.5%
rate_of_return = 0.025  # 2.5%

Tips_yield_h15 = [0, 0.005, 0.0075, 0.009, 0.01]  # Tips_5, Tips_7, Tips_10, Tips_20, Tips_30]
h15_years = [5, 7, 10, 20, 30]

payment = 1000

unit = 1000  # payment
# In[4]:
# TIPS Rates & Annuiity Prices tab
max_tips_year = 30
Tips_yield = np.zeros(max_tips_year)
Years = [x + 1 for x in range(max_tips_year)]
TIPS_structure = np.interp(Years, h15_years, Tips_yield_h15)

mortality_rate = pd.read_csv('mortality.csv')
# age range from 21 to 122, first index at 21. Assumptino is mortality rate <= 20 is zero
m_mortality_rate = mortality_rate['Male'].values
f_mortality_rate = mortality_rate['Female'].values

# First tab

# generate arrays from current age to end draw
# variables

size = 80
future_TIPS_Spread = 0
gender = 'f'

# investment = np.zeros(size)
# investment_proceeds = np.zeros(size)
# payment_override = np.zeros(size)
age = [x for x in range(current_age + 1, size + current_age + 1)]
print(age)
inheritance = np.zeros(size)
payment = np.zeros(size)
# reduced_payment = np.zeros(size)
principal = np.zeros(size)
coupon = np.zeros(size)
prob_survival = np.zeros(size)
prob_dying = np.zeros(size)
prob_death = np.zeros(size)
# joint_survival = np.zeros(size)
# prob_sec_dying = np.zeros(size)
# prob_sec_death = np.zeros(size)
annuity_payment = np.zeros(size)
annuity_cost = np.zeros(size)
discount = np.zeros(size)
annuity_purchase = np.zeros(size)
annuity_benefit = np.zeros(size)
total_cost = np.zeros(size)
tips_cost = np.zeros(size)
annuity_cost = np.zeros(size)
annuity_cost2 = np.zeros(size)
TIPS = np.zeros(size)
# prob_dying_m = np.zeros(size)
# prob_dying_f = np.zeros(size)
# total_cost2 = np.zeros(size)

# prob_survival_m = np.zeros(size)
# prob_survival_f = np.zeros(size)

# calculations for First tab
first_len = size
# inheritance goes back ward
i = first_len - 1
TIPS[i] = TIPS_structure[i] if i < len(TIPS_structure) else 0

payment[i] = 1000 / math.pow(1 + inflation_savings, i) if age[i] <= end_draw and age[i] >= current_age else 0
coupon[i] = payment[i] * TIPS[i]
principal[i] = payment[i] - coupon[i]
inheritance[i] = coupon[i]

for i in range(first_len - 2, -1, -1):
    if i == 30:
        print(31)
    payment[i] = 1000 / math.pow(1 + inflation_saving, i) if age[i] >= current_age and age[i] <= end_draw else 0
    TIPS[i] = TIPS_structure[i] if i < len(TIPS_structure) else 0
    sum_coupon = sum(coupon[i + 1:])
    principal[i] = (payment[i] - sum_coupon) / (1 + TIPS[i])
    coupon[i] = principal[i] * TIPS[i]
    inheritance[i] = inheritance[i + 1] + principal[i]
print(coupon)

i = 0

if gender == 'f':
    prob_dying[i] = f_mortality_rate[age[i] - 1]
else:
    prob_dying[i] = m_mortality_rate[age[i] - 1]
prob_survival[0] = 1 - prob_dying[0]
annuity_payment[0] = 1000

discount[i] = 1 / (1 + rate_of_return)
annuity_cost[i] = prob_survival[i] * annuity_payment[i] * discount[i]
prob_death[i] = prob_dying[0]
annuity_purchase[0] = 0
for i in range(1, first_len):
    prob_dying[i] = m_mortality_rate[age[i] - 1] if gender == 'm'else f_mortality_rate[age[i] - 1]
    prob_survival[i] = prob_survival[i - 1] * (1 - prob_dying[i])
    prob_death[i] = prob_survival[i - 1] * prob_dying[i]
    annuity_payment[i] = annuity_payment[i - 1] * (1 + worst_case_inflation - inflation_savings)
    discount[i] = discount[i - 1] / (1 + rate_of_return)
    annuity_cost[i] = prob_survival[i] * annuity_payment[i] * discount[i]
    annuity_purchase[i] = annuity_cost[i] if age[i - 1] > current_age and payment[i] == 0 else 0
    annuity_benefit[i] = 0 if annuity_purchase[i] == 0 else annuity_payment[i]

annuity_cost_scalar = sum(annuity_purchase)
annuity_cost2[0] = annuity_cost_scalar
tips_cost[0] = inheritance[0]
total_cost[0] = tips_cost[0] + annuity_cost2[0]

for i in range(1, end_draw-current_age):
    annuity_cost2[i] = annuity_cost_scalar/(prob_survival[i - 1] * discount[i - 1])
    tips_cost[i] = inheritance[i]
    total_cost[i] = tips_cost[i] + annuity_cost2[i]

TIPS_cost_scalar = inheritance[0]
total_cost_scalar = annuity_cost_scalar + TIPS_cost_scalar

df = pd.DataFrame({'age': age,
                   'inheritance': inheritance,
                   'payment': payment,
                   'principal': principal,
                   'coupon': coupon,
                   'prob_survival': prob_survival,
                   'prob_dying': prob_dying,
                   'prob_death': prob_death,
                   'TIPS': TIPS,
                   'annuity_payment': annuity_payment,
                   'annuity_cost': annuity_cost,
                   'discount': discount,
                   'annuity_purchase': annuity_purchase,
                   'annuity_benefit': annuity_benefit,
                   'total_cost': total_cost,
                   'tips_cost': tips_cost,
                   'annuity_cost2': annuity_cost2
                   })
df.to_csv('out2.csv', header=True,
          columns=['age', 'inheritance', 'payment', 'principal', 'coupon', 'prob_survival', 'prob_dying',
                   'prob_death', 'TIPS', 'annuity_payment', 'annuity_cost', 'discount', 'annuity_purchase',
                   'annuity_benefit', 'total_cost', 'tips_cost',  'annuity_cost2'], index=True)

from IPython.display import display

display(df)

print(df.to_html)

print(total_cost_scalar)
print(annuity_cost_scalar)
print(TIPS_cost_scalar)
