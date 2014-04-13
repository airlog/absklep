
var loginForm = {
    show: function() {
        $("#fullscreen-dim").show();
        $("#login-form-dialog").show();

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
        $("#login-form-dialog").hide();
        $(document).unbind("keyup");
    },
};

var registerForm = {
    onPreRegister: function() {
        console.log("registerForm.onPreRegister");
    },
};

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

var addCommentForm = {
    _stars: '#stars-comment-form',
    _inputRate: '#comment-form input[name=rate]',
    _inputComment: '#comment-form table tr td textarea[name=comment]',
    _activeColor: '#DBF723',
    _inactiveColor: 'black',
    
    clickStar: function(value) {
        var stars = $(this._stars).children();
        var input = $(this._inputRate).attr('value', value);        

        for (var i = 0; i < stars.length; i++) {
            if (i < value) stars[i].style.color = this._activeColor;
            else stars[i].style.color = this._inactiveColor;
        }
    },
    
    clear: function() {
        var stars = $(this._stars).children();
        $(this._inputRate).attr('value', 0);
        $(this._inputComment).val('');
                
        for (var i = 0; i < stars.length; i++) {
            stars[i].style.color = this._inactiveColor;
        }
    },
};

var cartView = (function() {
    var dialog = {
        show: function() {
            $("#fullscreen-dim").show();
            $("#added-to-cart-dialog").show();

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
            $("#added-to-cart-dialog").hide();
            $(document).unbind("keyup");
        },
    };

    var recount = function() {
	    var elements = document.getElementsByName("product");
		var sum = 0;

		for (var i=0; i<elements.length; i++) {
            var pid = elements[i].children[0].value;
            var p = elements[i].children[2].innerHTML;
            var x = elements[i].children[3].children[0].value;

            elements[i].children[4].innerHTML = x * parseFloat(p) + " PLN";
            sum += x * parseFloat(p);

			// uaktualnij koszyk
			cart.update(pid, x);
			
			// jeśli 0, usuń z koszyka
			if (x == 0) {
			    cart.remove(pid);
			    $(elements[i]).remove();
			}
		}

	    document.getElementById("Sum").innerHTML = sum.toFixed(2) + " PLN";
    }
    
    /**
     * Usuwa dany wiersz z tabeli.
     * 
     * Jeśli podany argument jest null to usuwa wszystkie wiersze z
     * tabeli. Uwaga, zmiana zagnieżdżenia elementów wymaga przerobienia tej metody.
     */
    var clear = function(ele) {
        if (ele == null) {
            $("tr[name=product]").remove();
            cart.clear();
            this.recount();
        } else {
            $(ele).parent().parent().remove();
            this.recount();
        }
    };

    return {
        recount: recount,
        dialog: dialog,
        clear: clear,
    };
})();

function createGui() {
    $("#fullscreen-dim").hide();
    $("#login-form-dialog").hide();
    $('#added-to-cart-dialog').hide();
}

