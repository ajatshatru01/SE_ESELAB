# SE_ESELAB
This is the implementation of the "cash withdrawal" usecase of the ATM system

# How to run this
1. Clone the repo
2. Activate the venv using the command:- source venv/bin/activate
3. Download all the necessary dependencies using the command:- pip install pytest openpyxl pytest-cov
4. To run the tests:- python -m pytest test_black_box.py test_white_box.py -v
5. To run whitebox testing with coverage:- python -m pytest test_white_box.py --cov=atm_system --cov-report=term-missing -v
6. To generate the excekl sheet consisting of the blackbox and whitebox tests:- python generate_excel.py
7. To run the system manually:- python main.py
8. Then enter the credentials, for now i have only stored two accounts credentials, they are :- card_number="4111111111111111": pin="1234";  card_number="4222222222222222":pin="5678"
9. Then choose 1 to withdraw money and in amount, put amount of multiple of 100 and less than 10000
10. Bingo! The transaction reciept will be displayed on the cli

# What all is there is in this repo
I have already included the test results output as a pdf in the repo to ease things up, along with this, i have also uploaded the excel sheet consisting of the list of blackbox and whitebox tests, i have already included the venv environment in the repo for ease
