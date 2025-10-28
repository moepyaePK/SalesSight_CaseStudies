# Test Plan of Sprint 2

## 1. Introduction & Scope

This section outlines the specific test cases for the key user stories being developed in Sprint 2. Our primary goal is to ensure the reliability, correctness, and usability of the new features. These detailed test cases will guide both manual testing efforts and the development of automated tests, minimizing defects and enhancing user satisfaction.

### Project: SalesSight

### Author(s):
Khun Shine Si Thu, Ei Thiri Aung, Soe Moe Ko , Moe Pyae Pyae Kyaw, Chan Myae Zaw, Yoon Moh Moh Aung, Min Swam Pyae, Pyae Phyo Paing, Min Khant Than Swe

### Date Created: October 17, 2025

## 2. Feature: User Registeration and Log-in

User Story: "As an SME owner, I want to create an account for my business, so that I can save my data and don't need to repeat the whole process when I enter the website."


| ID      | Title                | Preconditions | Test Steps                     | Expected Result                                  |
|---------|----------------------|------------------------|------------------------------------|--------------------------------------------------|
| RL-001  | (Happy Path) Account Registration           | -                 | 1. Navigate to the website.<br/>2. Click "Register".<br/>3. Enter username, email, password and confirm password in the correct format.<br/>4. Click "Register".                  | -User successfully register for their account and lands on log in page.<br/>-Account information is saved to the database.|
| RL-002  | (Happy Path) User Log In           | User already created an account on the website.                 | 1. Navigate to the website.<br/>2. Click "Login".<br/>3. Enter email and password.<br/>4. Click "Login".                  | User successfully land on the upload tab of of home page. |
| RL-003  | (Sad Path) Dashboard & Sales Forecasting – Cache Cleared After Login          | No CSV data file has been uploaded to the system after Login.                 | 1. Navigate to the website.<br/>2. Login and navigate to Dashboard or Sale Forecasting.                  | -Cached data is lost after login refresh.<br/>-Dashboard and Forecasting pages show an error message.<br/>-Previously viewed results are not retained.<br/>-User must upload the CSV file again to continue.     |

