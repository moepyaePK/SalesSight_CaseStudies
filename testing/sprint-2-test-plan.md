1. Introduction & Scope

This section outlines the specific test cases for the key user stories being developed in Sprint 2. Our primary goal is to ensure the reliability, correctness, and usability of the new features. These detailed test cases will guide both manual testing efforts and the development of automated tests, minimizing defects and enhancing user satisfaction.

Project: SalesSight

Author(s): Khun Shine Si Thu, Ei Thiri Aung, Soe Moe Ko , Moe Pyae Pyae Kyaw, Chan Myae Zaw, Yoon Moh Moh Aung, Min Swam Pyae, Pyae Phyo Paing, Min Khant Than Swe

Date Created: October 17, 2025

2. Feature: User Registeration and Log-in

User Story: "As an SME owner, I want to create an account for my business, so that I can save my data and don't need to repeat the whole process when I enter the website."


| ID      | Title                | Preconditions | Test Steps                     | Expected Result                                  |
|---------|----------------------|------------------------|------------------------------------|--------------------------------------------------|
| RL-001  | Account Registration           | -                 | 1. Navigate to the website./n2. Click "Regoster"./n3. Enter username, email, password and confirm password in the correct format./n4. Click "Register".                  | User successfully register for their account and lands on log in page. |
| TC-002  | Create Lead          | REQ-02                 | User is logged in                  | New lead is created and visible in lead list     |
| TC-003  | Search Leads         | REQ-03                 | At least one lead exists           | Search returns matching leads                    |
| TC-004  | Export Report        | REQ-05                 | Reports module accessible          | CSV export downloads with correct data           |
| TC-005  | Permission Enforcement| REQ-04                | Two roles exist (admin/user)       | Restricted actions blocked for unauthorized role |


3. Feature: Sale File Upload

User Story: "As a Head Judge, I want to see all Q Grader scores for a single sample and set a final, official score, so that I can resolve disagreements and finalize the evaluation."


| ID      | Title                | Preconditions | Test Steps                     | Expected Result                                  |
|---------|----------------------|------------------------|------------------------------------|--------------------------------------------------|
| TC-001  | User Login           | REQ-01                 | Test user exists                   | User successfully logs in and lands on dashboard |
| TC-002  | Create Lead          | REQ-02                 | User is logged in                  | New lead is created and visible in lead list     |
| TC-003  | Search Leads         | REQ-03                 | At least one lead exists           | Search returns matching leads                    |
| TC-004  | Export Report        | REQ-05                 | Reports module accessible          | CSV export downloads with correct data           |
| TC-005  | Permission Enforcement| REQ-04                | Two roles exist (admin/user)       | Restricted actions blocked for unauthorized role |
