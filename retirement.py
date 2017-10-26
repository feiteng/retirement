from flask import Flask, render_template, redirect, request
import numpy as np
import pandas as pd

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/plan', methods=['POST'])
def plan():
    style = request.form['style']
    if style == 'personal':
        return render_template('personal.html')
    return render_template('couple.html')


@app.route('/personal', methods=['POST'])
def signUpSingle():
    age = request.form['age']
    gender = request.form['gender']
    amount = request.form['curr_amount']
    spending = request.form['spending']
    calc( age=age, gender=gender, amount=amount, spending=spending)
    # return render_template('calc.html', age=age, gender=gender, amount=amount, spending=spending)


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
    return render_template('calc2.html', age=age, gender=gender, amount=amount, spending=spending)


def calc(age, gender, amount, spending):
    # Tips_5 = -0.0003
    # Tips_7 = 0.0024
    # Tips_10 = 0.0035
    # Tips_20 = 0.0069
    # Tips_30 = 0.0072

    # In[3]:

    Tips_yield_h15 = [0, 0.005, 0.0075, 0.009, 0.001]  # Tips_5, Tips_7, Tips_10, Tips_20, Tips_30]
    h15_years = [5, 7, 10, 20, 30]

    # In[4]:

    Max_tips_year = 30
    Tips_yield = np.zeros(Max_tips_year)
    Years = [x + 1 for x in range(Max_tips_year)]

    # In[5]:

    Tips_yield = np.interp(Years, h15_years, Tips_yield_h15)
    print(Tips_yield)

    # Let's bootstrap the discount factor from the yield, assuming all the tips are traded at par, so yield = coupon

    # In[6]:

    Tips_DF = np.zeros(Max_tips_year)
    Tips_DF[0] = 1 / (1 + Tips_yield[0])
    sum_df = Tips_DF[0]
    for i in range(1, Max_tips_year):
        Tips_DF[i] = (1 - Tips_yield[i] * sum_df) / (1 + Tips_yield[i])
        sum_df += Tips_DF[i]
    print(Tips_DF)



    # Let's calculate forward rate from the DF

    # In[7]:
    # foward price notused?
    #
    # Tips_fwd = np.zeros(Max_tips_year)
    # Tips_fwd[0] = Tips_yield[0]
    # for i in range(1, Max_tips_year):
    #     Tips_fwd[i] = Tips_DF[i - 1] / Tips_DF[i] - 1
    # # print(Tips_fwd)


    # In[20]:

    worst_case_inflation = 0.03     #   3%
    annuity_investment_return = 0.0255  #   2.5%
    # not used  # over_30yr_Tips = -0.01

    # In[21]:

    mortality_rate = pd.read_csv('mortality.csv')
    # print(mortality_rate)
    # Let's get user age and sex; also his/her additional saving

    # In[22]:

    current_age = int(age)
    swith_age = 95

    sex = 'Male'
    inflation_saving = 0

    # In[23]:

    unit = 1000

    # In[24]:

    age = [x for x in range(current_age + 1, swith_age + 1)]
    print('age')
    print(age)


    # In[25]:

    total_inheritance = np.zeros(Max_tips_year)

    for i in range(Max_tips_year):
        if i == 0:
            total_inheritance[i] = sum(Tips_DF[i:]) * unit
        else:
            total_inheritance[i] = sum(Tips_DF[i:]) / Tips_DF[i - 1] * unit
    print(total_inheritance)


    # Let's put probability of death into the account

    # In[26]:

    prob_death = np.array(mortality_rate.loc(mortality_rate['age'] > current_age))

    # In[27]:

    male_dying_prob = mortality_rate[mortality_rate.age > current_age]['Male'].values
    print(male_dying_prob)
    # In[28]:

    female_dying_prob = mortality_rate[mortality_rate.age > current_age]['Female'].values

    # In[29]:

    death_prob = np.zeros(len(male_dying_prob))
    death_prob[0] = male_dying_prob[0]
    survival_prob = np.zeros(len(male_dying_prob))
    survival_prob[0] = 1 - death_prob[0]

    # In[32]:

    for i in range(1, len(survival_prob)):
        death_prob[i] = survival_prob[i - 1] * male_dying_prob[i]
        survival_prob[i] = survival_prob[i - 1] * (1 - male_dying_prob[i])

    # print((death_prob))


    # In[33]:

    expected_inheritance = sum(total_inheritance * death_prob[:30])
    # print(expected_inheritance)


    # By far the prob of death and inheritance is corrected built in. The next step is to calculate the annuity cost

    # In[34]:

    # print(survival_prob)


    # In[144]:

    annuity_payment = np.asarray(
        [pow(1 + inflation_saving + worst_case_inflation, x) * unit for x in range(len(survival_prob))])
    # print(annuity_payment)


    # In[145]:

    annuity_discount = np.asarray([pow(1 + annuity_investment_return, -(x + 1)) for x in range(len(survival_prob))])

    # In[146]:

    annuity_cost = annuity_payment * annuity_discount * survival_prob
    # print(annuity_cost)


    # In[140]:

    annuity_purchase_mask = np.ones(len(survival_prob))
    annuity_purchase_mask[0:len(age)] = 0

    # In[141]:

    annuity_purchase = annuity_cost * annuity_purchase_mask

    # In[142]:

    total_annuity_cost = annuity_purchase.sum()

    # In[162]:

    # print(total_annuity_cost)
    total_cost = total_annuity_cost + total_inheritance[0]
    # print(total_cost)
    return [total_cost, total_inheritance[0], total_annuity_cost]


if __name__ == '__main__':
    app.run()
