// Dashboard JavaScript

// Confirm Delete
function confirmDelete() {
    return confirm("Are you sure you want to delete this certificate?");
}

// Success Alert
function showSuccess(message) {
    alert(message);
}

// Search Table
function searchTable() {
    let input = document.getElementById("searchInput");
    let filter = input.value.toUpperCase();
    let table = document.getElementById("certificateTable");
    let tr = table.getElementsByTagName("tr");

    for (let i = 1; i < tr.length; i++) {
        let td = tr[i].getElementsByTagName("td")[0];

        if (td) {
            let txtValue = td.textContent || td.innerText;

            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

// Preview Uploaded Image
function previewImage(event) {
    let output = document.getElementById("preview");

    if (output) {
        output.src = URL.createObjectURL(event.target.files[0]);
        output.style.display = "block";
    }
}

// Current Date & Time
function updateTime() {
    let now = new Date();

    let dateTime = now.toLocaleString();

    let time = document.getElementById("datetime");

    if (time) {
        time.innerHTML = dateTime;
    }
}

setInterval(updateTime, 1000);

// Dashboard Cards Animation
window.onload = function () {

    updateTime();

    let cards = document.querySelectorAll(".card");

    cards.forEach((card, index) => {

        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";

        setTimeout(() => {
            card.style.transition = "0.5s";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, index * 200);

    });

};