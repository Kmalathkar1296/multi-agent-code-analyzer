// Example JavaScript with issues

function authenticateUser(username, password) {
    var query = "SELECT * FROM users WHERE user='" + username + "'";  // SQL injection
    
    fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify({username, password})
    })
    .then(response => response.json());  // No catch!
    
    eval(userCode);  // Dangerous!
    console.log("Debug:", query);  // Remove in production
}

// Using == instead of ===
if (user == null) {
    console.log("No user");
}

// innerHTML XSS risk
document.getElementById('result').innerHTML = userInput;