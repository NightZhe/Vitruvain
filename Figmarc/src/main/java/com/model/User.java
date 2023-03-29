package com.model;

public class User {
	protected int id;
	protected String username;
	protected String password;
	protected String sex;
	protected String email;
	
	public User() {
	}

	
	public User(String username, String password, String sex, String email) {
		super();
		this.username = username;
		this.password = password;
		this.sex = sex;
		this.email = email;
	}


	public User(int id, String username, String password, String sex, String email) {
		super();
		this.id = id;
		this.username = username;
		this.password = password;
		this.sex = sex;
		this.email = email;
	}


	public int getId() {
		return id;
	}


	public void setId(int id) {
		this.id = id;
	}


	public String getUsername() {
		return username;
	}


	public void setUsername(String username) {
		this.username = username;
	}


	public String getPassword() {
		return password;
	}


	public void setPassword(String password) {
		this.password = password;
	}


	public String getSex() {
		return sex;
	}


	public void setSex(String sex) {
		this.sex = sex;
	}


	public String getEmail() {
		return email;
	}


	public void setEmail(String email) {
		this.email = email;
	}
	
	
}
