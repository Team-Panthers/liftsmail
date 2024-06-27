# Contributing to Liftsmail

## How to Contribute

### 1.  Fork the Repository

- Fork the repository by clicking the "Fork" button at the top right of the repository page.
- Clone your forked repository to your local machine
  
  ```
      git clone https://github.com/your-username/liftsmail.git
      cd liftsmail
  ```


### 2. Set Up the Development Environment

-   Create and activate a virtual environment:
    ```
        python3 -m venv venv
        source venv/bin/activate
    ```

-   Install backend dependencies

    ```
        pip install -r requirements.txt
    ```

-   Run migrations:
    ```
        python manage.py migrate
    ```

### 3. Create a Branch
-   Create a new branch for your feature or bug fix:
    ```
        git checkout -b feature/your-feature-name
    ```

### 4. Make Your Changes
-   Implement your feature or bug fix.
-   Write tests to cover your changes.
-   Ensure all tests pass:
    
    ```
        python manage.py test
    ```

### 5. Commit Your Changes

-   Commit your changes with a descriptive commit message:
    ```
        git add .
        git commit -m "Description of your changes"
    ```

### 6. Push to Your Fork

-   Push your changes to your forked repository:
    ```
        git push origin feature/your-feature-name
    ```
  
### 7. Open a Pull Request

-   Go to the original repository and click on the "Pull Requests" tab.
-   Click the "New Pull Request" button.
-   Select your feature branch from your fork and compare it with the base branch of the original repository.
-   Fill out the pull request template and submit your pull request.

### 8. Code Review

-  Your pull request will be reviewed by a project maintainer. Please address any feedback or requested changes. Once approved, your pull     request will be merged into the main branch.


### 9. Update Your Fork
-  Keep your fork updated with the latest changes from the original repository:
```
        git remote add upstream https://github.com/original-owner/liftsmail.git
        git fetch upstream
        git merge upstream/main
```

#   Thank You
Thank you for contributing to Liftsmail! Your efforts are greatly appreciated.