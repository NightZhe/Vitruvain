package com.abc;


import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;

import com.dao.UserDAO;
import com.model.User;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import jakarta.servlet.RequestDispatcher;

public class UserServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
	private UserDAO userDAO;
	
	public void init() {
		userDAO = new UserDAO();
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		doGet(request, response);
	}

	protected void doGet(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		String action = request.getServletPath();
        System.out.print(action);
		try {
			switch (action) {
			case "/new":
				showNewForm(request, response);
				break;
			case "/insert":
				insertUser(request, response);
				break;
			case "/update":
				updateUser(request, response);
				break;
			default:
				break;
			}
		} catch (SQLException ex) {
			throw new ServletException(ex);
		}
	}
	
	private void showNewForm(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		jakarta.servlet.RequestDispatcher dispatcher = request.getRequestDispatcher("index.jsp");
		dispatcher.forward(request, response);
	}
	
	private void insertUser(HttpServletRequest request, HttpServletResponse response) 
			throws SQLException, IOException, ServletException {
		String username = request.getParameter("username");
		System.out.print(username);
		String password = request.getParameter("password");
		String sex = request.getParameter("sex");
		String email = request.getParameter("email");
		User usert = userDAO.selectAllUsers(username);
		
		HttpSession session = request.getSession();
		
		System.out.print(usert);
		System.out.print("this is on UserServlet");
		if(usert == null) {
			User user =new User(username, password, sex, email);
			userDAO.insertUser(user);
			session.setAttribute("successmessage", "Thank you for your register! Please login!");
			request.getRequestDispatcher("Index.jsp").forward(request, response);
			System.out.print(usert);
			
		}else {
			session.setAttribute("defaultmessage", "Please try another username, thank you~:)");
			request.getRequestDispatcher("Register.jsp").forward(request, response);
			
		};
		
		
		
//		User newUser = new User(username, password, sex, email);
//		userDAO.insertUser(newUser);
//		request.getRequestDispatcher("Index.jsp").forward(request, response);
	}

	private void updateUser(HttpServletRequest request, HttpServletResponse response) 
			throws SQLException, IOException {
		int id = Integer.parseInt(request.getParameter("id"));
		String username = request.getParameter("username");
		String password = request.getParameter("password");
		String sex = request.getParameter("sex");
		String email = request.getParameter("email");
		User book = new User(id, username, password, sex, email);
		userDAO.updateUser(book);
		response.sendRedirect("index.jsp");
	}

}
