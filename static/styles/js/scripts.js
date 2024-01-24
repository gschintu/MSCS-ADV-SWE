/*!
    * Start Bootstrap - SB Admin v7.0.7 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2023 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});

$(document).ready(function() {


    const editor_datatablesListCurrencies = new DataTable.Editor({
        ajax: '/crypto_list_update_data',
        idSrc:'id',
        fields: [
            {
                label: 'Active:',
                name: 'is_active'
            },
            {
                label: 'Code:',
                name: 'code'
            },
            {
                label: 'Description:',
                name: 'desc'
            },
            {
                
                label: 'Code AG:',
                name: 'code_AG'
            },
            {
                label: 'Code CG:',
                name: 'code_CG'
            },
            {
                label: 'Code FMP:',
                name: 'code_FMP'
            }
        ],
        table: '#datatablesListCurrencies'
    });
    
    const datatablesListCurrencies = new DataTable('#datatablesListCurrencies', {
        ajax: '/crypto_list_json',
         buttons: [
            { extend: 'create', editor_datatablesListCurrencies },
            { extend: 'edit', editor_datatablesListCurrencies },
            { extend: 'remove', editor_datatablesListCurrencies }
        ],

        columns: [
            {
                data: 'id',
                visible:false
            },
            { data: 'code' },
            {
                data: 'is_active',
                //className: 'select-checkbox',
                orderable: true
            },
            { data: 'desc' },
            { data: 'code_AG' },
            { data: 'code_CG' },
            { data: 'code_FMP' },
            // { data: 'position' },
            // { data: 'office' },
            // { data: 'start_date' },
            // { data: 'salary', render: DataTable.render.number(null, null, 0, '$') }
        ],
        dom: 'frtip',
        order: [[2, 'desc']],
        select: {
            style: 'os',
            selector: 'td:first-child'
        }
    });
     
    // Activate an inline edit on click of a table cell
    datatablesListCurrencies.on('click', 'tbody td:not(:first-child)', function (e) {
        editor_datatablesListCurrencies.inline(this, {
            onBlur: 'submit'
        });
    });

    //Users List
    const editor_datatableUserList = new DataTable.Editor({
        ajax: '/user_list_update_data',
        idSrc:'id',
        fields: [
            {
                label: 'ID:',
                name: 'id'
            },
            {
                label: 'Email:',
                name: 'email'
            },
            {
                label: 'Name:',
                name: 'name'
            },
            {
                
                label: 'Gross Income Range:',
                name: 'gross_income_range'
            },
            {
                label: 'Investment Amount:',
                name: 'investment_amount'
            },
            {
                label: 'Investment Risk:',
                name: 'investment_risk'
            },
            {
                label: 'Admin:',
                name: 'is_admin'
            }
        ],
        table: '#datatableUserList'
    });
    
    const datatableUserList = new DataTable('#datatableUserList', {
        ajax: '/user_list_json',
         buttons: [
            { extend: 'create', editor_datatableUserList},
            { extend: 'edit', editor_datatableUserList },
            { extend: 'remove', editor_datatableUserList }
        ],

        columns: [
            {
                data: 'id',
                visible:false
            },
            { data: 'email' },
            {data: 'name'},
            { data: 'gross_income_range', render: DataTable.render.number(null, null, 0, '$') },
            { data: 'investment_amount', render: DataTable.render.number(null, null, 0, '$') },
            { data: 'investment_risk'},
            {
                data: 'is_admin',
                defaultContent: '',
                className: 'select-checkbox',
                orderable: true        
            }
        ],
        dom: 'frtip',
        order: [[2, 'desc']],
        select: {
            style: 'os',
            selector: 'td:first-child'
        }
    });
     
    // Activate an inline edit on click of a table cell
    datatableUserList.on('click', 'tbody td:not(:first-child)', function (e) {
        editor_datatableUserList.inline(this, {
            onBlur: 'submit'
        });
    });

    //const datatable_CryptoRecommendation = new DataTable('#datatable_CryptoRecommendation');

    const datatable_FPM_CryptoHistory = new DataTable('#datatable_FPM_CryptoHistory');

} );

