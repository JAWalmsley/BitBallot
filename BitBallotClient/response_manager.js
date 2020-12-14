const queryString = window.location.search;
console.log(queryString);
const urlParams = new URLSearchParams(queryString);
let status = urlParams.get('status')
console.log(status)
switch (status) {
    case('Voted'):
        $("#title")[0].innerText = "Success";
        $("#message")[0].innerText = "Your vote was cast"
        break;
    case('Registered'):
        $("#title")[0].innerText = "Success";
        $("#message")[0].innerText = "You are now registered to vote";
        break;
    case('InvalidSignature'):
        $("#title")[0].innerText = "Invalid Signature";
        $("#message")[0].innerText = "Sorry, that password is not correct";
        break;
    case('UserNotRegistered'):
        $("#title")[0].innerText = "Invalid User ID"
        $("#message")[0].innerText = "Sorry, that user is not registered";
        break;
    case('InvalidKey'):
        $("#title")[0].innerText = "Invalid Key";
        $("#message")[0].innerText = "Sorry, there was a problem with your password";
        break;
    case('UserAlreadyRegistered'):
        $("#title")[0].innerText = "User Already Registered"
        $("#message")[0].innerText = "Sorry, that user already exists"
        break;
}