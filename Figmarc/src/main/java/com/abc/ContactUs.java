package com.abc;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import javax.swing.JOptionPane;

/**
 * Servlet implementation class ContactUs
 */
public class ContactUs extends HttpServlet {
	private static final long serialVersionUID = 1L;
    private static final String INSERT = "INSERT INTO contactus"+ "(name, email, message) VALUES"+"(?,?,?);";
    private static final String SELECT_ALL_NAME = "SELECT*FROM contactus WHERE name=?;";	
    static final String JDBC_DRIVER="com.mysql.jdbc.Driver";
    static final String DB_URL="jdbc:mysql://localhost:3306/mainproject?useUnicode=true&characterEncoding=utf-8";
    static final String USER="root";
    static final String PASS="12345678";

    
    /**
     * @see HttpServlet#HttpServlet()
     */
    public ContactUs() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		request.setCharacterEncoding("UTF-8");
		response.setContentType("text/html; charset=utf-8");
		PrintWriter pw =response.getWriter();
		String name = request.getParameter("name");
		String email = request.getParameter("email");
		String message =request.getParameter("message");
		
		Connection conn= null;
		Statement stmt= null;
		
		try {
			Class.forName("com.mysql.jdbc.Driver");
			
			System.out.println("Connecting to database");
			conn =DriverManager.getConnection(DB_URL,USER,PASS);
			System.out.println("Creating statement");
			}catch(SQLException e) {} catch (ClassNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			};
		try (PreparedStatement preparedStatement = conn.prepareStatement(INSERT);) {
			preparedStatement.setString(1, name);
			preparedStatement.setString(2, email);
			preparedStatement.setString(3, message);
			System.out.println(preparedStatement);
			preparedStatement.executeUpdate();
		} catch (SQLException e) {}
		
    	try(PreparedStatement preparedStatement = conn.prepareStatement(SELECT_ALL_NAME);){
        	preparedStatement.setString(1, name);
        	System.out.println(preparedStatement);
        	System.out.println("this is on userdao");
        	ResultSet rs = preparedStatement.executeQuery();
			if(rs.next()){
//				pw.print("Welcome"+ name);
//				JOptionPane.showMessageDialog(null, "Thank you for your comment!");
				request.getRequestDispatcher("index.html").forward(request, response);
			}
			else {
//				JOptionPane.showMessageDialog(null, "Thank you for your comment! but please try again!");
				request.getRequestDispatcher("contact.html").include(request, response);
			}
			}catch(SQLException se){se.printStackTrace();	
			}catch(Exception e){e.printStackTrace();
			}finally {try {
				if(stmt!=null)
					stmt.close();
			}catch(SQLException se2) {}
			try {
				if(conn!=null)
					conn.close();
			}catch(SQLException se) {
				se.printStackTrace();
			}
			}
			
			
			pw.close();
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doGet(request, response);
	}

}
