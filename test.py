from flask import Response, Flask, render_template
import threading
import argparse
import datetime, time
import imutils
import cv2

outputFrame = None
lock = threading.Lock()
app = Flask(__name__)










"""
class user:
    name = ''
    email = ''
    password = ''
    login = False#


    def login (self):
      email = input('enter email address')
        password = input('enter password')

        if email== self.email and password == self.password:
            login =True
            print('login successful')
        else:
            print('login failed')

    def logout(self):
        login = False
        print('logged out')

    def isloggedin(self):
        if self.login:
            return True
        else:
            return False

    def profile(self):
    """
'''
# print("20 days are " +str(50) +" minutes")
calculation_to_seconds = 24*60*60
name_of_units = 'seconds'
'''

'''
def to_convert_units(number_of_days):  # like 20 number input value.
    return (f"{number_of_days}days are {number_of_days*calculation_to_seconds} {name_of_units}")



def validate_and_execute():
    try:
    #if user_input.isdigit():  # if user_input's  is number then execute the
        # below code else print the text of else statement.
        user_input_number = int(user_input)  # user_input string variable convert to number
        if user_input_number > 0:
            calculated_value = to_convert_units(user_input_number)
            print(calculated_value)
        elif user_input_number == 0:
            print("You entered a value is 0")
    except ValueError:
    #else:
        print("The entered value is not a number,so don't ruin my programme")

while True:
    user_input = input("Enter a number of days and I will convert it in to seconds: \n")
    # input function is holded user_input variable  #string input
    validate_and_execute()
'''



