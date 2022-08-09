function showExtraData(abstract, title) {
    // check if the abstract is not displayed
    if (document.getElementById(abstract).style.display == "none") {
        // display the abstract
        document.getElementById(abstract).style.display = "table-cell";

        // add the web URL hyperlink
        setTimeout(function() {
            document.getElementById(title).setAttribute("href", title);
            document.getElementById(title).setAttribute("target", "_blank");
            document.getElementById(title).style.color = "black";
        }, 10);
    }
    
    else {
        // hide the abstract
        document.getElementById(abstract).style.display = "none";

        // remove the web URL hyperlink
        setTimeout(function() {
            document.getElementById(title).removeAttribute("href");
        }, 10);
    }
}