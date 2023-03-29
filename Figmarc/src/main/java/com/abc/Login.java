package com.abc;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;

import java.io.IOException;
import java.io.PrintWriter;

import org.apache.jasper.tagplugins.jstl.core.Out;

import com.mysql.cj.exceptions.RSAException;

import java.io.*;
import jakarta.servlet.*;
import java.sql.*;

/**
 * Servlet implementation class Login
 */
public class Login extends HttpServlet {
	private static final long serialVersionUID = 1L;
       static final String JDBC_DRIVER="com.mysql.jdbc.Driver";
       static final String DB_URL="jdbc:mysql://localhost:3306/mainproject?useSSL=false";
       static final String USER="root";
       static final String PASS="12345678";
    /**
     * @see HttpServlet#HttpServlet()
     */
    public Login() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		request.setCharacterEncoding("UTF-8");
		response.setContentType("text/html; charset=utf-8");
		PrintWriter pw =response.getWriter();
		String name = request.getParameter("username");
		String password =request.getParameter("password");
		Connection conn= null;
		Statement stmt= null;
		
		try {
		Class.forName("com.mysql.jdbc.Driver");
		System.out.println("Connecting to database");
		conn =DriverManager.getConnection(DB_URL,USER,PASS);
		System.out.println("Creating statement");
		
	    //pw.print(name);
		String sql;
		sql ="SELECT password FROM usert WHERE username='"+name+"';";

		PreparedStatement qqqq = conn.prepareStatement(sql);
		ResultSet rs=qqqq.executeQuery();
		String psfsql =null;
		while(rs.next()) {
			psfsql =rs.getString("password");
		}
		rs.close();
		qqqq.close();
		conn.close();
		if(password.equals(psfsql)){
//			pw.print("Welcome"+ name);
			request.getRequestDispatcher("index.html").forward(request, response);
		}
		else {
			pw.print("<script> alert(\"請您重新輸入帳號密碼!\");</script>");
			request.getRequestDispatcher("Index.jsp").include(request, response);
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
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doPost(request, response);
	}

}
