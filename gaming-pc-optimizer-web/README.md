# Gaming PC Optimizer Web

## Overview
The Gaming PC Optimizer Web application is designed to help users clean temporary files, optimize their Windows settings for gaming, and launch games with high priority. This web application replicates the functionality of a desktop application in a user-friendly web interface.

## Project Structure
```
gaming-pc-optimizer-web
├── src
│   ├── index.html          # Main HTML document for the web application
│   ├── css
│   │   └── styles.css      # Styles for the web application
│   ├── js
│   │   ├── app.js          # Entry point for JavaScript functionality
│   │   ├── utils.js        # Utility functions for the application
│   │   └── optimizer.js     # Functions for optimization features
│   └── assets
│       └── icons           # Icon assets for the application
├── package.json            # Configuration file for npm
└── README.md               # Documentation for the project
```

## Setup Instructions
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd gaming-pc-optimizer-web
   ```

2. **Install dependencies:**
   ```
   npm install
   ```

3. **Run the application:**
   You can use a local server to run the application. For example, you can use the `live-server` package:
   ```
   npx live-server src
   ```

## Usage
- Open the application in your web browser.
- Use the interface to clean temporary files, enable game mode, and launch games.
- Monitor the activity log for updates on the optimization process.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.