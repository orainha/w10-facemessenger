//Credits to W3C: How TO - Filter/Search List
//https://www.w3schools.com/howto/howto_js_filter_lists.asp

(function () {
    'use strict'
    
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
    

})();