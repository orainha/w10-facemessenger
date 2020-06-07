//Credits to W3C: How TO - Filter/Search List
//https://www.w3schools.com/howto/howto_js_filter_lists.asp

(function () {
    'use strict'
    

    function search(input, elements, cols_number) {
        // Declare variables
        var filter, column, i, j, txtValue;
        filter = input.value.toUpperCase();
        // Loop through all list items, and hide those who don't match the search query
        for (i = 0; i < elements.length; i++) {
            for (j = 0; j <= cols_number; j++)
            {
                column = elements[i].getElementsByTagName("td")[j]
                txtValue = column.textContent || column.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    elements[i].style.display = "";
                    break;
                }else{
                    if (j == cols_number) elements[i].style.display = "none";
                }
            }
        }
    }


    function searchConversations() {
        // Declare variables
        var input, filter, tbody_trs, id_col, name_col, i, txtValue;
        input = inputSearchConversations
        filter = input.value.toUpperCase();
        tbody_trs = document.getElementsByClassName("conversation-group")
        
        // Loop through all list items, and hide those who don't match the search query
        for (i = 0; i < tbody_trs.length; i++) {
            id_col = tbody_trs[i].id
          
            // XXX (orainha) Find a better way to do this..
            txtValue = id_col;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tbody_trs[i].style.display = "";
            } else {
                for (let j=1; j<tbody_trs[i].children.length; j++)
                {
                    name_col = tbody_trs[i].children[j].children[1];
                    txtValue = name_col.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tbody_trs[i].style.display = "";
                        console.log(txtValue + " " + txtValue.toUpperCase().indexOf(filter))
                    }else{
                        tbody_trs[i].style.display = "none";
                    }
                }
            }
        }
    }


    function searchMessages() {
        // Declare variables
        var input, filter, tbody_trs, message_text, i, txtValue;
        input = inputSearchMessages
        filter = input.value.toUpperCase();
        tbody_trs = document.getElementsByClassName("div-message")
        // Loop through all list items, and hide those who don't match the search query
        for (i = 0; i < tbody_trs.length; i++){
            message_text = tbody_trs[i].children[0];
            txtValue = message_text.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tbody_trs[i].parentElement.parentElement.style.display = "";
            } else{
                tbody_trs[i].parentElement.parentElement.style.display = "none";
            }
        }
    }


    var inputSearchContacts = document.getElementById("inputSearchContacts")
    if (inputSearchContacts != null)
    {
        let elements = document.getElementById("tableContacts").getElementsByTagName("tbody")[0].children
        let cols_number = 3
        inputSearchContacts.addEventListener('keyup', function(){search(inputSearchContacts, elements, cols_number)});
    }
    
    
    var inputSearchImages = document.getElementById("inputSearchImages")
    if (inputSearchImages != null)
    {
        let elements = document.getElementById("tableImages").getElementsByTagName("tbody")[0].children
        let cols_number = 2
        inputSearchImages.addEventListener('keyup', function(){search(inputSearchImages, elements, cols_number)});
    }


    var inputSearchConversations = document.getElementById("inputSearchConversations")
    if (inputSearchConversations != null)
    {
        inputSearchConversations.addEventListener('keyup', searchConversations);
    }


    var inputSearchMessages = document.getElementById("inputSearchMessages")
    if (inputSearchMessages != null)
    {
        inputSearchMessages.addEventListener('keyup', searchMessages);
    }
    

})();