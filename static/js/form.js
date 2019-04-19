// // Variables
// var signupButton = document.getElementById('heel'),
//     loginButton = document.getElementById('login-button'),
//     userForms = document.getElementById('user_options-forms');

// var sign = document.getElementById('new-button');

// console.log("Hello");

// var btn = document.getElementById("jug");

// // Add event listener to the "Sign Up" button
// sign.addEventListener('click', () => {
//     userForms.classList.remove('login-click')
//     userForms.classList.add('signup-click')
// }, false)


// // Add event listener to the "Login" button
// loginButton.addEventListener('click', () => {
//     userForms.classList.remove('signup-click')
//     userForms.classList.add('login-click')
// }, false)
var signupButton = document.getElementById("new-button");
var userForms = document.getElementById('user_options-forms');

signupButton.addEventListener('click', function () {
    userForms.classList.remove('login-click');
    userForms.classList.add('signup-click');
})