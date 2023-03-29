package com.dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import com.model.User;

public class UserDAO {
	private String jdbcURL = "jdbc:mysql://localhost:3306/mainproject?useSSL=false";
	private String jdbcUsername = "root";
	private String jdbcPassword = "12345678";

	private static final String INSERT_USERT_SQL = "INSERT INTO usert" + "  (username, password, sex, email) VALUES "
			+ " (?, ?, ?, ?);";
	//private static final String SELECT_USER_BY_ID = "select id,username,password, sex,email from usert where id =?";
	//private static final String SELECT_ALL_USERT = "select * from usert";
	//private static final String DELETE_USERT_SQL = "delete from usert where username = ?;";
	private static final String UPDATE_USERT_SQL = "update usert set username = ?,email= ?, sex =? where id = ?;";
	private static final String SELECT_ALL_USERT = "SELECT*FROM usert WHERE username=?;";
       
    public UserDAO() {
        
    }
    //連接----------------------------------------------------------------------------------------------------
	protected Connection getConnection() {
		Connection connection = null;
		try {
			Class.forName("com.mysql.jdbc.Driver");
			connection = DriverManager.getConnection(jdbcURL, jdbcUsername, jdbcPassword);
		} catch (SQLException e) {
			e.printStackTrace();
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
		}
		return connection;
	}
	//找出usert所有資料-------------------------------------------------------------------------------------
    public User selectAllUsers(String username)throws SQLException{
    	User usert =null;
    	try(Connection connection = getConnection();
    		PreparedStatement preparedStatement = connection.prepareStatement(SELECT_ALL_USERT);){
    		preparedStatement.setString(1, username);
    		System.out.println(preparedStatement);
    		System.out.println("this is on userdao");
    		ResultSet rs = preparedStatement.executeQuery();
    		
    		while(rs.next()) {
    			int id = rs.getInt("id");
    			String password =rs.getString("password");
    			String sex =rs.getString("sex");
    			String email=rs.getString("email");
    			usert = new User(id, username, password, sex, email);
    		}
    	}catch(SQLException e) {
    		printSQLException(e);
    	}
    			return usert;
    } 
	//增加-------------------------------------------------------------------------------
	public void insertUser(User user) throws SQLException {
		System.out.println(INSERT_USERT_SQL);
		// try-with-resource statement will auto close the connection.
		// "INSERT INTO usert" + "  (username, password, sex, email) VALUES "+ " (?, ?, ?, ?);";
		try (Connection connection = getConnection();
			PreparedStatement preparedStatement = connection.prepareStatement(INSERT_USERT_SQL)) {
			preparedStatement.setString(1, user.getUsername());
			preparedStatement.setString(2, user.getPassword());
			preparedStatement.setString(3, user.getSex());
			preparedStatement.setString(4, user.getEmail());
			System.out.println(preparedStatement);
			preparedStatement.executeUpdate();
		} catch (SQLException e) {
			printSQLException(e);
		}
	}
	// 更新-------------------------------------------------------------------------------
	public boolean updateUser(User user) throws SQLException {
		boolean rowUpdated;
		
		// "update usert set username = ?,email= ?, sex =? where id = ?;";
		try (Connection connection = getConnection();
			PreparedStatement statement = connection.prepareStatement(UPDATE_USERT_SQL);) {
			statement.setString(1, user.getUsername());
			statement.setString(2, user.getEmail());
			statement.setString(3, user.getSex());
			statement.setInt(4, user.getId());

			rowUpdated = statement.executeUpdate() > 0;
		}
		return rowUpdated;
	}

	//印出錯誤-------------------------------------------------------------------------------------------------
	private void printSQLException(SQLException ex) {
		for (Throwable e : ex) {
			if (e instanceof SQLException) {
				e.printStackTrace(System.err);
				System.err.println("SQLState: " + ((SQLException) e).getSQLState());
				System.err.println("Error Code: " + ((SQLException) e).getErrorCode());
				System.err.println("Message: " + e.getMessage());
				Throwable t = ex.getCause();
				while (t != null) {
					System.out.println("Cause: " + t);
					t = t.getCause();
				}
			}
		}
	}
}
