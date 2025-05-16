
// Sidebar ToggleButton
const sideToggleButton = document.getElementById("sidebarToggleButton");
const sideNavBar = document.getElementById("sideNavBar");
const mainNavBar = document.getElementById("mainNavBar");

// Dealer
const dealerVar = document.getElementById("dealerID");
const dealerItems = document.getElementById("dealerItems");
const dealerCard = document.querySelector(".dealer__card");

// Medicine
const medicineVar = document.getElementById("medicineID");
const medicineItems = document.getElementById("medicineItems");
const medicineCard = document.querySelector(".medicine__card");

// Employee
const employeeVar = document.getElementById("employeeID");
const employeeItems = document.getElementById("employeeItems");
const employeeCard = document.querySelector(".employee__card");

// Customer
const customerVar = document.getElementById("customerID");
const customerItems = document.getElementById("customerItems");
const customerCard = document.querySelector(".customer__card");

// Purchase
const purchaseVar = document.getElementById("purchaseID");
const purchaseItems = document.getElementById("purchaseItems");
const purchaseCard = document.querySelector(".purchase__card");

// Confirm Logout Card
const confirmCard = document.querySelector(".confirm__card");

// Event Listeners
dealerVar.addEventListener("click", toggleDealerItems);
medicineVar.addEventListener("click", toggleMedicineItems);
employeeVar.addEventListener("click", toggleEmployeeItems);
customerVar.addEventListener("click", toggleCustomerItems);
purchaseVar.addEventListener("click", togglePurchaseItems);
sideToggleButton.addEventListener("click", toggleSideBar);


// Event Functions
function toggleDealerItems(e) {
    e.preventDefault();
    dealerItems.classList.add("d-none");
}

function toggleMedicineItems(e) {
    e.preventDefault();
    console.log("Clicked");
}

function toggleEmployeeItems(e) {
    e.preventDefault();
    console.log("Clicked");
}

function toggleCustomerItems(e) {
    e.preventDefault();
    console.log("Clicked");
}

function togglePurchaseItems(e) {
    e.preventDefault();
    console.log("Clicked");
}

function toggleSideBar(e) {
    mainNavBar.classList.toggle("margin__left");
    sideNavBar.classList.toggle("sidenav-d-none");
    // dealerCard.classList.toggle("d-none");
    // medicineCard.classList.toggle("d-none");
    // employeeCard.classList.toggle("d-none");
    // customerCard.classList.toggle("d-none");
    // purchaseCard.classList.toggle("d-none");
    // confirmCard.classList.toggle("d-none");
}