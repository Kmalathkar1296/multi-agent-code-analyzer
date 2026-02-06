// Example Java with issues

import java.sql.*;
import java.util.Random;

public class Example {
    public User findUser(String username) {
        // SQL injection vulnerability
        String query = "SELECT * FROM users WHERE name='" + username + "'";
        
        try {
            Connection conn = getConnection();
            Statement stmt = conn.createStatement();
            return stmt.executeQuery(query);
        } catch (Exception e) {
            // Empty catch - bad practice
        }
        
        return null;
    }
    
    public String generateToken() {
        // Insecure random
        Random rand = new Random();
        return String.valueOf(rand.nextInt());
    }
    
    public void processData(String data) {
        String result = "";
        // String concatenation in loop
        for (int i = 0; i < data.length(); i++) {
            result = result + data.charAt(i);
        }
    }
}