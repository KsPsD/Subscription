function callApi(plan) {
  const paymentDetails = {
    method_type: "credit_card",
    card_number: "4242-4242-4242-4242",
    expiration_date: "12/25",
    cvc: "123",
  };

  fetch("/api/subscriptions/subscribe/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"), // Fetch CSRF token for Django
    },
    body: JSON.stringify({
      plan_name: plan,
      payment_details: paymentDetails,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log(data);
      alert("성공: " + JSON.stringify(data)); // 성공 알림
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("실패: " + error); // 실패 알림
    });
}

// Function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
