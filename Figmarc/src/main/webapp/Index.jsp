<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8" errorPage="error.jsp"%>
<!DOCTYPE html>
<html>
<head>
<title>Index.jsp</title>
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
					<h2 style="color: whitesmoke;">請登入或註冊</h2>
					<form name="login" action="Login" method="post">
						<script type="text/javascript">
							
						<%--對輸入的賬號資訊進行判斷，賬號密碼不能為空且必須輸入驗證碼--%>
							function validate() {
								if (login.username.value == "") {
									alert("帳號不能為空");
									return;
								}
								if (login.password.value == "") {
									alert("密碼不能為空");
									return;
								}
								login.submit();
							}
						</script>
						<%
						String name = (String) session.getAttribute("successmessage");
						if (name == "Thank you for your register! Please login!") {
							out.print("<script> alert(\"註冊成功，請重新登入~謝謝\");</script>");
						}
						request.getSession().invalidate();
						%>

						<div class="inputBox">

							<input type="text" name="username" placeholder="帳號" value="">
						</div>
						<div class="inputBox">
							<input type="password" name="password" placeholder="密碼" value="">
						</div>

						<div class="inputBox">
							<input type="button" value="登入" onclick="validate()">
							<input type="button" value="註冊" onclick="window.location.href='Register.jsp'">
						</div>
				</div>

				</form>
				<!--<div class="inputBox">
					<form name="register" action="Register.jsp" method="get">
						<input type="submit" value="regitser" >
					</form>
					</div>-->


				</div>
			</div>
	</section>
</body>
</html>