// This listens for the exact moment the user clicks the "Submit" button on the registration form.
document.querySelector("form").addEventListener("submit", function(event){
    
    // Finds the privacy/consent checkbox on the page so we can check its status.
    let consent = document.getElementById("consent");

    // Checks if the user forgot to check the consent box.
    if(!consent.checked){
        
        // Stops the form from sending their data to the server (blocks the page from reloading).
        event.preventDefault();
        
        // Pops up a custom warning window on the screen telling them they need to agree to the terms.
        document.getElementById("popup").style.display = "flex";
    }
});

// This is a helper function that runs when the user clicks the "Close" button inside the warning popup.
function closePopup(){
    
    // Hides the warning window completely so they can go back to filling out the form.
    document.getElementById("popup").style.display = "none";
}