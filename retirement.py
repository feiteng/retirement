from flask import Flask, render_template, redirect, request
import numpy as np
import pandas as pd

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/homePage', methods=['POST'])
def getHomePage():
    return render_template('index.html')


@app.route('/plan', methods=['POST'])
def plan():
    style = request.form['style']
    if style == 'personal':
        return render_template('personal.html')
    return render_template('couple.html')


@app.route('/personal', methods=['POST'])
def signUpSingle():
    age = int(request.form['age'])
    gender = request.form['gender']
    amount = int(request.form['curr_amount'])
    spending = int(request.form['spending'])
    x = calc(age, gender)  # , amount, spending)
    return render_template('calc.html', x=x)


@app.route('/couple', methods=['POST'])
def signUpCouple():
    age1 = request.form['age1']
    gender1 = request.form['gender1']
    age2 = request.form['age2']
    gender2 = request.form['gender2']
    age = [age1, age2]
    gender = [gender1, gender2]
    amount = request.form['curr_amount']
    spending = request.form['spending']
    x = calcJoint(age, gender)  # , amount, spending)
    return render_template('calc2.html',x=x)

def calcJoint(_current_age, _gender):  ##, amount, spending):
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
    c_age = list(map(int, _current_age))  # vector
    current_age = c_age[0]
    age_difference = c_age[0] - c_age[1]
    gender = _gender  # vector

    firstPerson = calc(c_age[0], gender[0])
    secondPerson = calc(c_age[1], gender[1])

    # inflation_saving = 0
    end_draw = 95
    percentage_on_survival = 0.5
    pct_joint_annuity = percentage_on_survival * 2 - 1
    pct_individual_annuiity = 1 - percentage_on_survival

    draw = 50000
    inflation_savings = 0
    investment = 2200000

    # RA inputs
    worst_case_inflation = 0.03
    standard_deviation = 0.0961

    average_return = 0.04
    annuity_investment_return = 0.025  # 2.5%
    rate_of_return = 0.025  # 2.5%

    Tips_yield_h15 = [0, 0.005, 0.0075, 0.009, 0.01]  # Tips_5, Tips_7, Tips_10, Tips_20, Tips_30]
    h15_years = [5, 7, 10, 20, 30]

    unit_payment = 1000

    # TIPS Rates & Annuiity Prices tab
    max_tips_year = 30
    # Tips_yield = np.zeros(max_tips_year)
    Years = [x + 1 for x in range(max_tips_year)]
    TIPS_structure = np.interp(Years, h15_years, Tips_yield_h15)

    mortality_rate = pd.read_csv('mortality.csv')
    # age range from 21 to 122, first index at 21. Assumptino is mortality rate <= 20 is zero
    m_mortality_rate = mortality_rate['Male'].values
    m_survival_rate = np.ones(len(m_mortality_rate))
    m_survival_rate_lookup = np.ones(len(m_mortality_rate))
    for i in range(21, len(m_mortality_rate)):
        m_survival_rate[i] = m_survival_rate[i - 1] * (1 - m_mortality_rate[i])
        m_survival_rate_lookup[i] = (m_survival_rate[i] + m_survival_rate[i - 1]) / 2

    f_mortality_rate = mortality_rate['Female'].values
    f_survival_rate = np.ones(len(f_mortality_rate))
    f_survival_rate_lookup = np.ones(len(m_mortality_rate))
    for i in range(21, len(f_mortality_rate)):
        f_survival_rate[i] = f_survival_rate[i - 1] * (1 - f_mortality_rate[i])
        f_survival_rate_lookup[i] = (f_survival_rate[i] + f_survival_rate[i - 1]) / 2

    # First tab

    # generate arrays from current age to end draw
    # variables

    size = 80
    future_TIPS_Spread = 0

    survive0 = m_survival_rate_lookup if gender[0] == 'm' else f_survival_rate_lookup
    survive1 = m_survival_rate_lookup if gender[0] == 'm' else f_survival_rate_lookup
    # vec_survive = [survive0, survive1]

    investment = np.zeros(size)
    investment_proceeds = np.zeros(size)
    # payment_override = np.zeros(size)
    age = [x for x in range(current_age + 1, size + current_age + 1)]
    print(age)
    inheritance = np.zeros(size)
    payment = np.zeros(size)
    reduced_payment = np.zeros(size)
    principal = np.zeros(size)
    coupon = np.zeros(size)
    prob_survival = np.zeros(size)
    prob_dying = np.zeros(size)
    prob_death = np.zeros(size)
    joint_survival = np.zeros(size)
    joint_survival_tmp = np.zeros(len(f_mortality_rate))
    joint_survival_full = np.zeros(len(f_mortality_rate))

    i = 0
    joint_survival_tmp[i] = 1 - (1 - survive0[i - 1]) * (1 - survive1[i - 1])
    joint_survival_full[i] = joint_survival_tmp[i]

    for i in range(1, len(f_mortality_rate)):
        joint_survival_tmp[i] = 1 - (1 - survive0[i - 1]) * (1 - survive1[i - 1])
        joint_survival_full[i] = (joint_survival_tmp[i - 1] + joint_survival_tmp[i]) / 2

    prob_sec_dying = np.zeros(size)
    prob_sec_death = np.zeros(size)
    annuity_payment = np.zeros(size)
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
    total_cost_x = np.zeros(size)

    # prob_survival_m = np.zeros(size)
    # prob_survival_f = np.zeros(size)

    # calculations for First tab
    first_len = size
    # inheritance goes back ward
    i = first_len - 1
    TIPS[i] = TIPS_structure[i] if i < len(TIPS_structure) else 0

    payment[i] = unit_payment / math.pow(1 + inflation_savings, i) if age[i] <= end_draw and age[i] >= current_age else 0
    reduced_payment[i] = max(0, payment[i] - investment_proceeds[i])
    coupon[i] = payment[i] * TIPS[i]
    principal[i] = payment[i] - coupon[i]
    inheritance[i] = coupon[i]

    investment_proceeds[0] = investment[0]
    for i in range(1, first_len):
        payment[i] = unit_payment / math.pow(1 + inflation_savings, i) if age[i] >= current_age and age[i] <= end_draw else 0
        investment_proceeds[i] = max(0, investment_proceeds[i - 1] * (1 + future_TIPS_Spread) + investment[i] - payment[i])

    for i in range(first_len - 2, -1, -1):
        payment[i] = unit_payment / math.pow(1 + inflation_savings, i) if age[i] >= current_age and age[i] <= end_draw else 0
        reduced_payment[i] = max(0, payment[i] - investment_proceeds[i])
        TIPS[i] = TIPS_structure[i] if i < len(TIPS_structure) else 0
        sum_coupon = sum(coupon[i + 1:])
        principal[i] = max(0, (payment[i] - sum_coupon) / (1 + TIPS[i]))
        coupon[i] = principal[i] * TIPS[i]
        inheritance[i] = inheritance[i + 1] + principal[i]

    i = 0

    if gender == 'f':
        prob_dying[i] = f_mortality_rate[age[i] - 1]
    else:
        prob_dying[i] = m_mortality_rate[age[i] - 1]
    prob_survival[0] = 1 - prob_dying[0]
    annuity_payment[0] = unit_payment
    prob_sec_dying[0] = 1 - joint_survival[0]
    discount[i] = 1 / (1 + rate_of_return)
    annuity_cost[i] = prob_survival[i] * annuity_payment[i] * discount[i]
    prob_death[i] = prob_dying[0]
    annuity_purchase[0] = 0
    for i in range(1, first_len):
        joint_survival[i] = joint_survival_full[age[i] - 1]
        prob_dying[i] = m_mortality_rate[age[i] - 1] if gender == 'm'else f_mortality_rate[age[i] - 1]
        prob_sec_dying[i] = (joint_survival[i - 1] - joint_survival[i]) / joint_survival[i - 1]
        prob_sec_death[i] = prob_sec_dying[i] * joint_survival[i - 1]
        prob_survival[i] = prob_survival[i - 1] * (1 - prob_dying[i])
        prob_death[i] = prob_survival[i - 1] * prob_dying[i]
        annuity_payment[i] = annuity_payment[i - 1] * (1 + worst_case_inflation - inflation_savings)
        discount[i] = discount[i - 1] / (1 + rate_of_return)
        annuity_cost[i] = prob_survival[i] * annuity_payment[i] * discount[i]
        annuity_purchase[i] = annuity_cost[i] if age[i - 1] > current_age and payment[i] == 0 else 0
        annuity_benefit[i] = 0 if annuity_purchase[i] == 0 else annuity_payment[i]

    i = 0
    annuity_cost_scalar = pct_joint_annuity * sum(annuity_purchase) + pct_individual_annuiity * (
        firstPerson.annuity_cost[0] + secondPerson.annuity_cost[0])
    annuity_cost2[0] = annuity_cost_scalar
    tips_cost[0] = inheritance[0]
    total_cost[0] = tips_cost[0] + annuity_cost2[0]
    total_cost_x[i] = total_cost[i] * draw / unit_payment

    for i in range(1, end_draw - current_age):
        annuity_cost2[i] = annuity_cost_scalar / (prob_survival[i - 1] * discount[i - 1])
        tips_cost[i] = inheritance[i]
        total_cost[i] = tips_cost[i] + annuity_cost2[i]
        total_cost_x[i] = total_cost[i] * draw / unit_payment

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
                       'annuity_cost2': annuity_cost2,
                       'end_draw': end_draw,
                       'cur_age': current_age
                       })
    # df.to_csv('out3.csv', header=True,
    #           columns=['age', 'inheritance', 'payment', 'principal', 'coupon', 'prob_survival', 'prob_dying',
    #                    'prob_death', 'TIPS', 'annuity_payment', 'annuity_cost', 'discount', 'annuity_purchase',
    #                    'annuity_benefit', 'total_cost', 'tips_cost', 'annuity_cost2'], index=True)
    #
    # print(total_cost_scalar)
    # print(annuity_cost_scalar)
    # print(TIPS_cost_scalar)

    return df


def calc(_current_age, _gender):  # , amount, spending):
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
    current_age = int(_current_age)
    sex = 'Male'
    inflation_saving = 0
    end_draw = 95
    percentage_on_survival = 0.5
    draw = 50000
    inflation_savings = 0
    investment = 2200000

    # RA inputs
    worst_case_inflation = 0.03
    standard_deviation = 0.0961

    average_return = 0.04
    annuity_investment_return = 0.025  # 2.5%
    rate_of_return = 0.025  # 2.5%

    Tips_yield_h15 = [0, 0.005, 0.0075, 0.009, 0.01]  # Tips_5, Tips_7, Tips_10, Tips_20, Tips_30]
    h15_years = [5, 7, 10, 20, 30]

    unit_payment = 1000

    # TIPS Rates & Annuiity Prices tab
    max_tips_year = 30
    # Tips_yield = np.zeros(max_tips_year)
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
    gender = _gender

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

    payment[i] = unit_payment / math.pow(1 + inflation_savings, i) if age[i] <= end_draw and age[i] >= current_age else 0
    coupon[i] = payment[i] * TIPS[i]
    principal[i] = payment[i] - coupon[i]
    inheritance[i] = coupon[i]

    for i in range(first_len - 2, -1, -1):
        if i == 30:
            print(31)
        payment[i] = unit_payment / math.pow(1 + inflation_saving, i) if age[i] >= current_age and age[i] <= end_draw else 0
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
    annuity_payment[0] = unit_payment

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

    for i in range(1, end_draw - current_age):
        annuity_cost2[i] = annuity_cost_scalar / (prob_survival[i - 1] * discount[i - 1])
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
                       'annuity_cost2': annuity_cost2,
                       'end_draw': end_draw,
                       'cur_age': current_age
                       })
    return df
    # df.to_csv('out2.csv', header=True,
    #           columns=['age', 'inheritance', 'payment', 'principal', 'coupon', 'prob_survival', 'prob_dying',
    #                    'prob_death', 'TIPS', 'annuity_payment', 'annuity_cost', 'discount', 'annuity_purchase',
    #                    'annuity_benefit', 'total_cost', 'tips_cost', 'annuity_cost2'], index=True)
    #
    # print(total_cost_scalar)
    # print(annuity_cost_scalar)
    # print(TIPS_cost_scalar)


if __name__ == "__main__":
    app.run(debug=True)
