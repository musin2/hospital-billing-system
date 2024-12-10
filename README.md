## Hospital Billing System

### Project Description

 This project is responsible for keeping track of the bills of a particular organization or insurance company. It accumulates the bills of patients that belong to a particular organization to keep track of how much that organization owes the hospital. The system can then generate invoices for organizations whenever they want to pay after a certain period (e.g. monthly or quarterly).

 For the project to run, it requires:


### Installation
- Clone the repository
    ```bash
    git clone https://github.com/musin2/hospital-billing-system.git
    cd hospital-billing-system
    ```

- Install the frontent dependencies in the client directory
    ```bash
    cd client
    npm install
    ```

- Navigate to the root of the project file
- Activate the virtual environment
    ```bash
    pipenv shell
    ```

- Install the backend dependencies in the virtual environment
    ```bash
    pipenv install
    ```

- Run the server
    ```bash
    flask run
    ```


- Run the frontend
    ```bash
    cd client
    npm run dev
    ```

### Usage
Users can manage the partner organizations, manage patients bills and generate invoices