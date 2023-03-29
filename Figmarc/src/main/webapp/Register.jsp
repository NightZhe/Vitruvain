<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8" errorPage="error.jsp"%>
<html>
<head>
<title>register</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="./assets/css/login.css">
  <!-- Favicons -->
  <link href="assets/img/arm.png" rel="icon">
  <link href="assets/img/arm.png" rel="apple-touch-icon">
</head>
<body>
	<section>
	<!-- 背景顏色 -->
		<div class="color"></div>
		<div class="color"></div>
		<div class="color"></div>
		<div class="box">
			<!-- 背景圓 -->
			<div class="circle" style="-x: 0"></div>
			<div class="circle" style="-x: 1"></div>
			<div class="circle" style="-x: 2"></div>
			<div class="circle" style="-x: 3"></div>
			<div class="circle" style="-x: 4"></div>
			<div class="circle" style="-x: 5"></div>
			<div class="circle" style="-x: 6"></div>
			<div class="circle" style="-x: 7"></div>
			<div class="circle" style="-x: 8"></div>
			<div class="circle" style="-x: 9"></div>
			
			<div class="container">
			<div class="form">
		<h1 style="color: white;">歡迎您進行註冊</h1>
		<%--action=RegisterServlet--%>
		<form name="register" action="insert" method="post">
			<script type="text/javascript">
				
			<%--對輸入的賬號資訊進行判斷，賬號密碼不能為空且必須輸入驗證碼--%>
				function validate() {
					if (register.username.value == "") {
						alert("帳號不能為空");
						return;
					}
					if (register.password.value == "") {
						alert("密碼不能為空");
						return;
					}
					if (register.sex.value == "") {
						alert("性別欄不能為空");
						return;
					}
					if (register.email.value == "") {
						alert("信箱不能為空");
						return;
					}
					register.submit();
				}
			</script>
			<%
			String name = (String) session.getAttribute("defaultmessage");
			if (name == "Please try another username, thank you~:)") {
				out.print("<script> alert(\"帳號重複，請重新設定!\");</script>");
			}
			request.getSession().invalidate();
			%> 
			<div class="inputBox"><input type="text" name="username" placeholder="請設定帳號"></div>
			<div class="inputBox"><input type="password" name="password" placeholder="請設定密碼"></div>
			<div class="inputBox"><input name="email" type="text" placeholder="請設定信箱 "></div>
			<div style="color:pink;" ><br>
			&nbsp&nbsp&nbsp&nbsp&nbsp請選擇性別：<input name="sex" type="radio" value="male" checked >男 
			 &nbsp&nbsp&nbsp<input name="sex" type="radio" value="female">女 
			</div>
			<div class="inputBox"><input type="button" id="leftbutton" value="註冊" onclick="validate()">&nbsp&nbsp&nbsp&nbsp&nbsp
			&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<input type="button" id="rightbutton" value="回登入頁" onclick="window.location.href='Index.jsp'"></div>
		</form>
		</div>
		</div>
	</div>
	</section>
</body>
</html>