document.addEventListener("DOMContentLoaded", function () {
  // Kakao JavaScript SDK의 초기화와 로그인 버튼에 이벤트 핸들러를 설정합니다.
  Kakao.init("8cd9a7b988003d6821148374f32e3cda");

  document
    .getElementById("kakao-login-btn")
    .addEventListener("click", function (event) {
      event.preventDefault(); // 추가된 코드
      console.log("Login button clicked");

      Kakao.Auth.login({
        success: function (authObj) {
          // 로그인 성공 시, 백엔드에 토큰을 전송합니다.
          console.log("Login successful");
          console.log(authObj);
          fetch("http://localhost:2200/login", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              access_token: authObj.access_token,
            }),
          })
            .then((response) => {
              if (!response.ok) {
                throw new Error(`POST request failed: ${response.status}`);
              }
              return response.json();
            })
            .then((data) => {
              console.log(data);
              if (data.message === "existing_user") {
                alert("이미 계정이 있습니다. 로그인되었습니다.");
              } else if (data.message === "new_user") {
                alert("새로운 계정으로 저장되었습니다.");
              } else {
                alert("알 수 없는 오류가 발생했습니다.");
              }

              localStorage.setItem("jwt", data.token);

              window.location.href = "/index";
            })
            .catch((error) => {
              console.error("Error:", error);
            });
        },
        fail: function (err) {
          console.log(err);
        },
      });
    });
});

document.addEventListener("DOMContentLoaded", function () {
  // 저장된 JWT 토큰이 있는지 확인합니다.
  const token = localStorage.getItem("jwt");

  if (token) {
    // 토큰이 있다면 백엔드 서버에 토큰을 전송하여 사용자 정보를 확인합니다.
    fetch("http://localhost:2200/welcome", {
      headers: {
        Authorization: "Bearer " + token,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          // 서버로부터 받은 환영 메시지를 상단바에 띄웁니다.
          const welcomeMessage = document.getElementById("welcome-message");
          welcomeMessage.innerHTML = data.message;
        } else {
          // 에러 메시지를 출력하거나 다른 처리를 할 수 있습니다.
          console.error("Could not retrieve welcome message");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    // 토큰이 없는 경우, 로그인되지 않았다는 것을 알리거나 로그인 페이지로 리다이렉트 할 수 있습니다.
    console.log("User is not logged in");
  }
});
