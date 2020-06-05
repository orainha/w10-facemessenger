//Credits to W3C: How TO - Filter/Search List
//https://www.w3schools.com/howto/howto_js_filter_lists.asp

(function () {
    'use strict'
    
    // XXX (orainha) - Can we merge searchContacts and searchImages in only one function?

    function searchContacts() {
        // Declare variables
        var input, filter, tbody_trs, id_col, name_col, email_col, phone_col, i, txtValue;
        input = inputSearchContacts
        filter = input.value.toUpperCase();
        tbody_trs = document.getElementById("tableContacts").getElementsByTagName("tbody")[0].children
        
        // Loop through all list items, and hide those who don't match the search query
        for (i = 0; i < tbody_trs.length; i++) {
            id_col = tbody_trs[i].getElementsByTagName("th")[0]
            name_col = tbody_trs[i].getElementsByTagName("td")[1];
            email_col = tbody_trs[i].getElementsByTagName("td")[2];
            phone_col = tbody_trs[i].getElementsByTagName("td")[3];
            
            // XXX (orainha) Find a better way to do this..
            txtValue = id_col.textContent || id_col.innerText ;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tbody_trs[i].style.display = "";
            } else {
                txtValue = name_col.textContent || name_col.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tbody_trs[i].style.display = "";
                }else{
                    txtValue = email_col.textContent || email_col.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tbody_trs[i].style.display = "";
                    }else{
                        txtValue = phone_col.textContent || phone_col.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            tbody_trs[i].style.display = "";
                        }else{
                            tbody_trs[i].style.display = "none";
                        }
                    }
    
                    // for (let j=1; j<=3;j++)
                    // {
                    //     let column = tbody_trs[i].getElementsByTagName("td")[j]
                    //     txtValue = column.textContent || column.innerText;
                    //     if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    //             tbody_trs[i].style.display = "";
                    //     }else{
                    //         if (j == 3)
                    //         {
                    //             tbody_trs[i].style.display = "none";
                    //         }
                            
                    //     }
                    // }
                }
            }
        }
    }

    function searchImages() {
        // Declare variables
        var input, filter, tbody_trs, source_col, file_col, date_col, i, txtValue;
        input = inputSearchImages
        filter = input.value.toUpperCase();
        tbody_trs = document.getElementById("tableImages").getElementsByTagName("tbody")[0].children
        
        // Loop through all list items, and hide those who don't match the search query
        for (i = 0; i < tbody_trs.length; i++) {
            source_col = tbody_trs[i].getElementsByTagName("td")[0]
            file_col = tbody_trs[i].getElementsByTagName("td")[1];
            date_col = tbody_trs[i].getElementsByTagName("td")[2];

            // XXX (orainha) Find a better way to do this..
            txtValue = source_col.textContent || source_col.innerText ;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tbody_trs[i].style.display = "";
            } else {
                txtValue = file_col.textContent || file_col.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tbody_trs[i].style.display = "";
                }else{
                    txtValue = date_col.textContent || date_col.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tbody_trs[i].style.display = "";
                    }else{
                        tbody_trs[i].style.display = "none";
                    }
    
                    // for (let j=0; j<3;j++)
                    // {
                    //     let column = tbody_trs[i].getElementsByTagName("td")[j]
                    //     txtValue = column.textContent || column.innerText;
                    //     if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    //             tbody_trs[i].style.display = "";
                    //     }else{
                    //         if (j == 3)
                    //         {
                    //             tbody_trs[i].style.display = "none";
                    //         }
                            
                    //     }
                    // }
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


    var inputSearchContacts = document.getElementById("inputSearchContacts")
    if (inputSearchContacts != null)
    {
        inputSearchContacts.addEventListener('keyup', searchContacts);
    }
        

    var inputSearchImages = document.getElementById("inputSearchImages")
    if (inputSearchImages != null)
    {
        inputSearchImages.addEventListener('keyup', searchImages);
    }


    var inputSearchConversations = document.getElementById("inputSearchConversations")
    if (inputSearchConversations != null)
    {
        inputSearchConversations.addEventListener('keyup', searchConversations);
    }
    

})();