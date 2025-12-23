/**
* Function: validateOnSave
* Purpose: Validates mandatory fields and prevents duplicate selections before saving.
*/
function validateOnSave(executionContext) {
    "use strict";
    var formContext = executionContext.getFormContext();
    var eventArgs = executionContext.getEventArgs();
    var status = formContext.getAttribute('dx_projectproductstage').getValue();
    var hasError = false;
 
    // Clear previous notifications
    formContext.getControl('dx_primarywonreason').clearNotification('won-mandatory');
    formContext.getControl('dx_primarylostreason').clearNotification('lost-mandatory');
    formContext.getControl('dx_competitor').clearNotification('comp-won');
    formContext.getControl('dx_competitor').clearNotification('comp-lost');
    formContext.getControl('dx_wonreason').clearNotification('won-duplicate');
    formContext.getControl('dx_lostreason').clearNotification('lost-duplicate');
    formContext.ui.clearFormNotification('save-block')
 
    // ✅ Mandatory checks
    if (status === 425420003 || status === 425420004) {
        var primaryWon = formContext.getAttribute('dx_primarywonreason').getValue();
        var competitor = formContext.getAttribute('dx_competitor').getValue();
        var otherWon = formContext.getAttribute('dx_wonreason').getValue();
 
        if (!primaryWon) {
            formContext.getControl('dx_primarywonreason').setNotification('Required', 'won-mandatory');
            hasError = true;
        }
        if (primaryWon && primaryWon !== 121960002 && !competitor) {
            formContext.getControl('dx_competitor').setNotification('Required', 'comp-won');
            hasError = true;
        }
    	if (primaryWon && otherWon && otherWon.includes(primaryWon)) {
            formContext.getControl('dx_wonreason').setNotification('Duplicate reason', 'won-duplicate');
            hasError = true;
    	}
    }
    else if (status === 425420006) {
        var primaryLost = formContext.getAttribute('dx_primarylostreason').getValue();
        var competitorLost = formContext.getAttribute('dx_competitor').getValue();
        var mandatoryLostReasons = [425420013, 425420007, 425420000, 425420005];
	var otherLost = formContext.getAttribute('dx_lostreason').getValue();
 
        if (!primaryLost) {
            formContext.getControl('dx_primarylostreason').setNotification('Required', 'lost-mandatory');
            hasError = true;
        }
        if (primaryLost && mandatoryLostReasons.includes(primaryLost) && !competitorLost) {
            formContext.getControl('dx_competitor').setNotification('Required', 'comp-lost');
            hasError = true;
        }
	if (primaryLost && otherLost && otherLost.includes(primaryLost)) {
            formContext.getControl('dx_lostreason').setNotification('Duplicate reason', 'lost-duplicate');
            hasError = true;
	}
    }
    // ✅ Block save if any error
    if (hasError && eventArgs) {
        formContext.ui.setFormNotification('Please fix errors before saving.', 'ERROR', 'save-block');
        eventArgs.preventDefault();
    }
}
 
/* ---------------- ORIGINAL FUNCTIONS CONTINUE ---------------- */
function calculateTotalDelQuantity(formContext, recordId) {
    "use strict";
    var totalDelQty = 0;
    Xrm.WebApi.retrieveMultipleRecords("dx_deliveryschedule", `?$select=dx_plannedquantity&$filter=_dx_projectproduct_value eq ${recordId} and statecode eq 0`).then(
        function success(result) {
            for (var i = 0; i < result.entities.length; i++) {
                totalDelQty += result.entities[i].dx_plannedquantity;
            }
            formContext.getAttribute("dx_totaldeliveryschedulequantity").setValue(totalDelQty);
            var qtyOnProduct = formContext.getAttribute("quantity").getValue();
            if (totalDelQty > qtyOnProduct) {
                formContext.getControl("dx_totaldeliveryschedulequantity").setNotification('should not be greater than product quantity.', '8198b16d-f7f7-49f7-a4cc-dd9c1f8dcc5c');
            } else {
                formContext.getControl("dx_totaldeliveryschedulequantity").clearNotification('8198b16d-f7f7-49f7-a4cc-dd9c1f8dcc5c');
            }
            setOrClearFormNotification(totalDelQty, qtyOnProduct, formContext);
        }
    );
}
 
function updatePlannedDates(executionContext) {
    "use strict";
    var formContext = executionContext.getFormContext();
    var closedate = formContext.getAttribute('dx_closedate').getValue();
    var recordId = formContext.data.entity.getId();
    Xrm.WebApi.retrieveMultipleRecords("dx_deliveryschedule", `?$select=dx_planneddate&$filter=_dx_projectproduct_value eq ${recordId}`).then(
        function success(result) {
            for (var i = 0; i < result.entities.length; i++) {
                var delPlannedDate = result.entities[i].dx_planneddate;
                var delId = result.entities[i].recordId;
            }
        }
    );
}
 
function validateQuantity(executionContext) {
    "use strict";
    var formContext = executionContext.getFormContext();
    formContext.getControl("dx_totaldeliveryschedulequantity").clearNotification('8198b16d-f7f7-49f7-a4cc-dd9c1f8dcc5c');
    var totalQuantity = formContext.getAttribute("dx_totaldeliveryschedulequantity").getValue();
    var qtyOnProduct = formContext.getAttribute("quantity").getValue();
    if (qtyOnProduct !== 0 && totalQuantity !== 0) {
        if (totalQuantity > qtyOnProduct) {
            formContext.getControl("dx_totaldeliveryschedulequantity").setNotification('should not be greater than product quantity.', '8198b16d-f7f7-49f7-a4cc-dd9c1f8dcc5c');
        } else {
            formContext.getControl("dx_totaldeliveryschedulequantity").clearNotification('8198b16d-f7f7-49f7-a4cc-dd9c1f8dcc5c');
        }
        setOrClearFormNotification(totalQuantity, qtyOnProduct, formContext);
    }
}
 
function setListPrice(executionContext) {
    "use strict";
    var formContext = executionContext.getFormContext();
    var product = formContext.getAttribute('productid').getValue();
    if (product !== null) {
        var prodId = product[0].id.replace(/[{}]/g, '');
        Xrm.WebApi.retrieveRecord("product", prodId, "?$select=_pricelevelid_value").then(
            function success(result) {
                if (result && result._pricelevelid_value) {
                    Xrm.WebApi.retrieveMultipleRecords("productpricelevel", `?$select=amount&$filter=_pricelevelid_value eq ${result._pricelevelid_value} and _productid_value eq ${prodId}`).then(
                        function success(resultpl) {
                            if (resultpl) {
                                var amount = 0;
                                for (var i = 0; i < resultpl.entities.length; i++) {
                                    amount += resultpl.entities[i].amount;
                                }
                                formContext.getAttribute('dx_listprice').setValue(amount);
                            }
                        }
                    );
                }
            }
        );
    }
}
 
function setDefaultValueForReporting(executionContext) {
    "use strict";
    var formContext = executionContext.getFormContext();
    var opportunity = formContext.getAttribute('opportunityid').getValue();
    if (opportunity) {
        var recordId = opportunity[0].id.replace(/[{}]/g, '');
        Xrm.WebApi.retrieveMultipleRecords("opportunityproduct", `?$select=quantity&$filter=_opportunityid_value eq ${recordId}`).then(
            function success(result) {
                if (result.entities.length === 0) {
                    formContext.getAttribute("dx_valueforreporting").setValue(true);
                }
            }
        );
    }
}
 
function setOrClearFormNotification(totalQuantity, qtyOnProduct, formContext) {
    "use strict";
    if (totalQuantity !== qtyOnProduct) {
        formContext.ui.setFormNotification(`Quantity mismatch. Remaining quantity ${qtyOnProduct - totalQuantity}`, 'WARNING', '9198b16d-f7f7-49f7-a4cc-dd9c1f8dcc5c');
    } else {
        formContext.ui.clearFormNotification('9198b16d-f7f7-49f7-a4cc-dd9c1f8dcc5c');
    }
}
 
function refreshOnLoad(executionContext) {
    "use strict";
    var formContext = executionContext.getFormContext();
    if (formContext) {
        formContext.data.refresh(true);
    }
}
