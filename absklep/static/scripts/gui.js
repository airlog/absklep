
var loginForm = {
    show: function() {
        $("#fullscreen-dim").show();
        $("#login-form").show();

        var that = this;
        $(document).keyup(function(e) {
            console.log("escape pressed");
            if (e.keyCode == 27) {  // esc key
                that.hide();
            }
        });
    },

    hide: function() {
        $("#fullscreen-dim").hide();
        $("#login-form").hide();
        $(document).unbind("keyup");
    },
};

var registerForm = {
    onPreRegister: function() {
        console.log("registerForm.onPreRegister");
    },
};

function createGui() {
    $("#fullscreen-dim").hide();
    $("#login-form").hide();
}

var addProductForm = {
    _addedPropertiesCount: 0,

    newProperty: function() {
        var template = $("#add-product-form #template-property");
        var instance = template.clone();
        var td = instance.children();

        instance.attr('id', null);
        instance.removeClass('hidden');
        td[0].children[0].setAttribute('name', 'propertyKey' + this._addedPropertiesCount);
        td[1].children[0].setAttribute('name', 'propertyValue' + this._addedPropertiesCount);
        
        template
        .parent()
            .append(instance);
        
        this._addedPropertiesCount++;
        $("#add-product-form-properties-count").attr('value', '' + this._addedPropertiesCount);
        console.log(this._addedPropertiesCount);
    },
    
    onSubmit: function() {
        var form = $("#add-product-form");
        var properties = $('.add-product-form-data');
        
        console.log(form.serialize());
    },
};
    
