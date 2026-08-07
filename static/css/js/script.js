function togglePassword(){

let password=document.getElementById("password");
let eye=document.getElementById("eye");

if(password.type==="password"){

password.type="text";
eye.classList.remove("bi-eye");
eye.classList.add("bi-eye-slash");

}else{

password.type="password";
eye.classList.remove("bi-eye-slash");
eye.classList.add("bi-eye");

}

}