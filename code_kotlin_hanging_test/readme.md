# Temporal Template - Kotlin Hanging Test

This repository contains a template for testing Temporal workflows using Kotlin. The purpose of this template is to provide a starting point for writing and running tests for Temporal workflows.

## Getting Started

### Prerequisites

- [Kotlin](https://kotlinlang.org/)
- [Gradle](https://gradle.org/)
- [Temporal Server](https://docs.temporal.io/docs/server/quick-install/)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/gauravthadani/temporal-template.git
    ```
2. Navigate to the project directory:
    ```sh
    cd temporal-template/code_kotlin_hanging_test
    ```
3. Build the project:
    ```sh
    ./gradlew clean build shadowJar
    ```

### Running 

in the resources directory (here)[app/src/main/resources]
1) place ca.pem and ca.key
2) replace endpoint and namespace in `config.json`
3) re build, create shadowJar

from `temporal-template/code/app/build/libs` directory

Run worker
```bash
 java -jar app-all.jar --mode worker
```

Run starter
```bash
 java -jar app-all.jar --mode starter
```
## Project Structure

- `src/main/kotlin`: Contains the main source code for the Temporal workflows.
- `src/test/kotlin`: Contains the test cases for the Temporal workflows.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Temporal](https://temporal.io/)
- [Kotlin](https://kotlinlang.org/)
