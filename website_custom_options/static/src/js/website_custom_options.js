/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
// import variantmixin from "@website_sale_stock/js/variant_mixin";
import { formatCurrency } from "@web/core/currency";
import { rpc } from "@web/core/network/rpc";

if (!$('.oe_website_sale').length) {
    return $.Deferred().reject("DOM doesn't contain '.oe_website_sale'");
}
// $('.js_custom_option_multiple_change').select2()
function price_to_str(price) {
    // var l10n = _t.database.parameters;
    // var precision = 2;

    // if ($(".decimal_precision").length) {
    //   precision = parseInt($(".decimal_precision").last().data('precision'));
    // }
    // var formatted = sprintf('%.' + precision + 'f', price).split('.');
    // formatted[0] = utils.insert_thousand_seps(formatted[0]);
    return formatCurrency(price)
    // return price.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function isString(o) {
    return typeof o === "string";
}

function calculatePrice($ul, combination) {
    var $combinationPrice = combination.price;
    var $parent = $ul.closest('.js_product');
    var $product_id = $parent.find('.product_id').first().val();
    var $price = $parent.find(".oe_price:first .oe_currency_value");
    var $website_price = $parent.find("[itemprop='price']");

    if ($combinationPrice === undefined) {
        $combinationPrice = parseFloat($website_price.text().replace('‑', '-'));
    }

    var $option_data = $ul.data("option_data");
    var $actual_option_data = $ul.data("actual_option_data");
    var $actual_option_value_data = $ul.data("actual_option_value_data");
    if (isString($option_data)) {
        $option_data = JSON.parse($option_data.replace(/'/g, '"'));
        $ul.data('option_data', $option_data);
    }
    var $option_value_data = $ul.data("option_value_data");
    if (isString($option_value_data)) {
        $option_value_data = JSON.parse($option_value_data.replace(/'/g, '"'));
        $ul.data('option_value_data', $option_value_data);
    }
    var $option_public_data = $ul.data("option_public_data");
    if (isString($option_public_data)) {
        $option_public_data = JSON.parse($option_public_data.replace(/'/g, '"'));
        $ul.data('option_public_data', $option_public_data);
    }
    var $option_value_public_data = $ul.data("option_value_public_data");
    if (isString($option_value_public_data)) {
        $option_value_public_data = JSON.parse($option_value_public_data.replace(/'/g, '"'));
        $ul.data('option_value_public_data', $option_value_public_data);
    }


    if ($.isEmptyObject($option_data)) {
        return 0;
    }

    var $disableButton = false;
    var $additionalPrice = 0;
    var $additionalPublicPrice = 0;
    var $actualPrice = 0
    $parent.find("input.js_custom_option_change, textarea.js_custom_option_change").each(function () {
        var $input = $(this);
        var optionId = $input.attr('option_id');
        var isRequired = $input.attr('is_required');
        var inputData = $input.val();
        if (inputData) {
            var $customOptionPrice = $option_data[optionId]
            var $actualOptionPrice = $actual_option_data[optionId]
            if ($customOptionPrice) {
                $additionalPrice = $additionalPrice + parseFloat($customOptionPrice);
                $actualPrice = $actualPrice + parseFloat($actualOptionPrice);
            }
            var $customOptionPrice = $option_public_data[optionId]
            if ($customOptionPrice) {
                $additionalPublicPrice = $additionalPublicPrice + parseFloat($customOptionPrice);
            }
        } else if (isRequired == "True") {
            $disableButton = true;
        };
    });
    $parent.find("select.js_custom_option_multiple_change").each(function () {
        var $input = $(this);
        var isRequired = $input.attr('is_required');
        var inputData = $input.val();
        var $customOptionPrice = 0.0;
        var $actualOptionPrice = 0.0;
        var $customOptionPublicPrice = 0.0;
        if (inputData && inputData.length > 0) {
            $.each($input.find(":selected"), function () {
                var $selectedOption = $(this);
                var $selectedOptionPrice = $option_value_data[$selectedOption.val()];
                var $actualselectedOptionPrice = $actual_option_value_data[$selectedOption.val()];
                $customOptionPrice = $customOptionPrice + parseFloat($selectedOptionPrice);
                $actualOptionPrice = $actualOptionPrice + parseFloat($actualselectedOptionPrice);
                var $selectedOptionPublicPrice = $option_value_public_data[$selectedOption.val()];
                $customOptionPublicPrice = $customOptionPublicPrice + parseFloat($selectedOptionPublicPrice);
            });
            if ($customOptionPrice) {
                $additionalPrice = $additionalPrice + parseFloat($customOptionPrice);
                $actualPrice = $actualPrice + parseFloat($actualOptionPrice);
                // console.log("actualPrice", $actualPrice)

            }
            if ($customOptionPublicPrice) {
                $additionalPublicPrice = $additionalPublicPrice + parseFloat($customOptionPublicPrice);
            }
        } else if (isRequired == "True") {
            $disableButton = true;
        };
    });

    $parent.find("input.js_custom_option_checkbox_change").each(function () {
        var radio_type = "radio";
        var checkbox_type = "checkbox";
        if (radio_type == $(this).attr("type")) {
            var $input = $(this);
            var inputData = $input.val();
            var if_checked = $input.prop("checked")
            var isRequired = $input.attr('is_required');
            if (if_checked) {
                if (inputData) {
                    var $selectedOption = $(this);
                    var $customOptionPrice = $option_value_data[$selectedOption.val()]
                    var $actualOptionPrice = $actual_option_value_data[$selectedOption.val()]

                    if ($customOptionPrice) {
                        $additionalPrice = $additionalPrice + parseFloat($customOptionPrice);
                        $actualPrice = $actualPrice + parseFloat($actualOptionPrice);

                    }
                    var $customOptionPublicPrice = $option_value_public_data[$selectedOption.val()]
                    if ($customOptionPrice) {
                        $additionalPublicPrice = $additionalPublicPrice + parseFloat($customOptionPublicPrice);
                    }
                }
            }
            else if (isRequired == "True") {
                var count = 0;
                $input.closest('ul').find('li').each(function () {
                    var $options = $(this).find('.js_custom_option_checkbox_change');
                    if (!$options.prop("checked")) {
                        if ($disableButton == false && count == 0) {
                            $disableButton = true;
                        }
                    }
                    else {
                        $disableButton = false;
                        count = 1;
                    }
                })
            };
        }
        else if (checkbox_type == $(this).attr("type")) {
            var $input = $(this);
            var inputData = $input.val();
            var if_checked = $input.prop("checked")
            var isRequired = $input.attr('is_required');
            if (if_checked) {
                if (inputData) {
                    var $selectedOption = $(this);
                    var $customOptionPrice = $option_value_data[$selectedOption.val()]
                    var $actualOptionPrice = $actual_option_value_data[$selectedOption.val()]

                    if ($customOptionPrice) {
                        $additionalPrice = $additionalPrice + parseFloat($customOptionPrice);
                        $actualPrice = $actualPrice + parseFloat($actualOptionPrice);
                        // console.log("actualPrice", $actualPrice)

                    }
                    var $customOptionPublicPrice = $option_value_public_data[$selectedOption.val()]
                    // if ($customOptionPrice){
                    //     $additionalPrice = $additionalPrice + parseFloat($customOptionPrice);
                    //     $actualPrice = $actualPrice + parseFloat($actualOptionPrice);

                    // }
                    if ($customOptionPublicPrice) {
                        $additionalPublicPrice = $additionalPublicPrice + parseFloat($customOptionPublicPrice);
                    }
                }
            }
            else if (isRequired == "True") {
                var count = 0;
                $input.closest('ul').find('li').each(function () {
                    var $options = $(this).find('.js_custom_option_checkbox_change');
                    if (!$options.prop("checked")) {
                        if ($disableButton == false && count == 0) {
                            $disableButton = true;
                        }
                    }
                    else {
                        $disableButton = false;
                        count = 1;
                    }
                })
            };
        }
        if ($disableButton == true) {
            return false;
        }
    });
    $price.html(price_to_str($combinationPrice + $additionalPrice));
    if ($parent.find(".product_price .oe_default_price .oe_currency_value").css('text-decoration', 'line-through')) {
        // var actual_price = parseFloat($parent.find(".product_price .oe_default_price .oe_currency_value").css('text-decoration','line-through').html())
        // actual_price = actual_price + $additionalPublicPrice
        var actual_price = combination['list_price'];
        // var actual_price = combination;
        actual_price = actual_price + $actualPrice
        $parent.find(".product_price .oe_default_price .oe_currency_value").css('text-decoration', 'line-through').html(price_to_str(actual_price));
    }
    if ($disableButton) {
        $parent.find("#add_to_cart").addClass("disabled");
    } else {
        $parent.find("#add_to_cart").removeClass("disabled");
    }
}

if (window.location.href.indexOf('shop/cart') > -1) {
    $(".td-price").find(".text-danger:not(.non_discount_option_price)").css("dispaly", "none !important");
}


$('.oe_website_sale').each(function () {
    var oe_website_sale = this;

    $(oe_website_sale).on('change', 'input.js_custom_option_change, textarea.js_custom_option_change, select.js_custom_option_multiple_change, input.js_custom_option_checkbox_change', function (ev) {
        var $ul = $(ev.target).closest('.js_add_cart_custom_options');
        $("ul[data-attribute_exclusions]").change();
    });
});


function get_custom_option(ev, combination, qty) {
    var multiple = []
    var dropdown = []
    var selectedOption = {}
    if ($('.js_add_cart_custom_options').children('li').children('select').length) {
        $('.js_add_cart_custom_options').children('li').children('select').each(function () {
            if ($(this).attr('multiple')) {
                multiple.push($(this).attr('option_id'))
                var selectedIndex = $(this).val();
                if (selectedIndex) {
                    selectedOption[$(this).attr('option_id')] = selectedIndex;
                }
            }
            else {
                dropdown.push($(this).attr('option_id'))
                var selectedIndex = $(this)[0].selectedIndex
                if (selectedIndex) {
                    selectedOption[$(this).attr('option_id')] = selectedIndex;
                }
            }
        })
    }
    rpc('/update/option/price', {
        combination, qty, multiple, dropdown
    }).then(function (result) {
        if (Object.keys(result).length) {
            const combination_price_info = result['combination_price_info'];
            $('.js_add_cart_custom_options').data('option_data', combination_price_info.option_data);
            $('.js_add_cart_custom_options').data('actual_option_data', combination_price_info.actual_option_data);
            $('.js_add_cart_custom_options').data('option_public_data', combination_price_info.option_public_data);
            $('.js_add_cart_custom_options').data('option_value_data', combination_price_info.option_value_data);
            $('.js_add_cart_custom_options').data('actual_option_value_data', combination_price_info.actual_option_value_data);
            $('.js_add_cart_custom_options').data('option_value_public_data', combination_price_info.option_value_public_data);
            let options = $('.js_add_cart_custom_options').children('li');
            if (options.length) {
                options.each(function () {
                    if ($(this).children('ul').length) {
                        $(this).children('ul').find('li').each(function () {
                            const price_data = combination_price_info['option_value_data'][parseInt($(this).find('input').val())];
                            if (price_data) {
                                const updated_price = combination_price_info['option_value_data'][parseInt($(this).find('input').val())]
                                $(this).find('.oe_currency_value').text(price_to_str(updated_price))
                            }
                        })
                    }
                    else if ($(this).children('select').length) {
                        $(this).children('select').each(function () {
                            if ($(this).attr('multiple') == 'multiple') {
                                const price_data = combination_price_info['multi_option_field_html'];
                                const $this = $(this)
                                if (price_data) {
                                    $.each(price_data, function (index, value) {
                                        if ($this.attr('option_id') == index) {
                                            $this.html(value)
                                        }
                                    })
                                }
                                if (selectedOption) {
                                    $.each(selectedOption, function (index, value) {
                                        if ($this.attr('option_id') == index) {
                                            $.each(value, function (index, val) {
                                                $this.find('option').each(function () {
                                                    if ($(this).val() == val) {
                                                        $(this).attr('selected', 'selected')
                                                    }
                                                })
                                            })
                                        }
                                    });
                                }
                            }
                            else {
                                const price_data = combination_price_info['dropdown_option_field_html'];
                                const $this = $(this)
                                if (price_data) {
                                    $.each(price_data, function (index, value) {
                                        if ($this.attr('option_id') == index) {
                                            $this.html(value)
                                        }
                                    })
                                }
                                if (selectedOption) {
                                    $.each(selectedOption, function (index, value) {
                                        if ($this.attr('option_id') == index) {
                                            $($this.find('option')[value]).attr('selected', 'selected')
                                        }
                                    });
                                }
                            }
                        })
                    }
                    else {
                        let option_id = $(this).children('strong').attr('data-oe-id');
                        if (option_id) {
                            let response = Object.keys(combination_price_info['option_data']).includes(option_id);
                            if (response) {
                                let price = combination_price_info['option_data'][option_id];
                                $(this).find('.oe_currency_value').text(price_to_str(price))
                            }
                        }
                    }
                })
            }
        }
        calculatePrice($('.js_add_cart_custom_options'), combination);
    });
}

publicWidget.registry.WebsiteSale.include({
    events: Object.assign({
        'change .js_add_cart_custom_options': '_onChangeCustomOptions',
    }, publicWidget.registry.WebsiteSale.prototype.events),


    _onChangeCustomOptions: function (ev) {
        let combinationData = $('.js_add_cart_variants').data('combination')
        calculatePrice($('.js_add_cart_custom_options'), combinationData);
    },

    _onChangeCombination: function (ev, $parent, combination) {
        var $super = this._super
        const qty = parseInt($('#product_details').find('input[name="add_qty"]').val());
        get_custom_option(ev, combination, qty)
        $('.js_add_cart_variants').data('combination', combination)
        var def = this._super.apply(this, arguments);
        return def;
    },


    _handleAdd: function ($form) {

        var self = this;
        this.$form = $form;

        var productSelector = [
            'input[type="hidden"][name="product_id"]',
            'input[type="radio"][name="product_id"]:checked'
        ];

        var productReady = this.selectOrCreateProduct(
            $form,
            parseInt($form.find(productSelector.join(', ')).first().val(), 10),
            $form.find('.product_template_id').val(),
            false
        );

        // Collect custom option data
        var wk_custom_options = {}
        var file_load_check = false
        var no_file = true

        $form.find('.js_add_cart_custom_options .custom_option').each(function (ev) {

            var wk_option = $(this)
            var input = wk_option.find('input')
            var type = input.attr('type')
            var checked_input = wk_option.find('input:checked')
            if (type) {
                if (type == 'radio') {
                    wk_custom_options[checked_input.attr('name')] = checked_input.val()
                }
                else if (type == 'checkbox') {
                    input.each(function () {
                        if ($(this).is(':checked')) {
                            wk_custom_options[$(this).attr('name')] = $(this).val()
                        }
                        else {
                            delete wk_custom_options[$(this).attr('name')]
                        }
                    });
                }
                else if (type == 'file') {
                    var file = input.prop('files')[0];
                    if (file) {
                        no_file = false
                        new Promise((resolve, reject) => {
                            var fr = new FileReader();
                            fr.onload = () => {
                                var data = fr.result;
                                wk_custom_options[input.attr('name')] = data
                                wk_custom_options['file_name'] = file.name;
                                file_load_check = true
                                resolve(data)
                            };
                            fr.readAsDataURL(file);
                        });
                    }
                    else {
                        delete wk_custom_options[input.attr('name')]
                        file_load_check = true
                    }
                }
                else if (type == 'date') {
                    if (input.val()) {
                        wk_custom_options[input.attr('name')] = input.val()
                    }
                }
                else if (type == 'datetime-local') {
                    if (input.val()) {
                        wk_custom_options[input.attr('name')] = input.val()
                    }
                }
                else if (type == 'time') {
                    if (input.val()) {
                        wk_custom_options[input.attr('name')] = input.val()
                    }
                }
                else {
                    wk_custom_options[input.attr('name')] = input.val()
                }
            }
            else {
                var textarea = wk_option.find('textarea')
                var select = wk_option.find('select')
                if (textarea.length != 0 && $.trim(textarea.val())) {
                    wk_custom_options[textarea.attr('name')] = textarea.val()
                }
                else if (select.length != 0) {
                    var selected = select.find('option:selected').val()
                    if (select[0].hasAttribute('multiple')) {
                        selected = select.find('option:selected').toArray().map(item => item.value);
                    }
                    if (selected.length != 0) {
                        wk_custom_options[select.attr('name')] = selected
                    }
                    else {
                        delete wk_custom_options[select.attr('name')]
                    }
                }
            }
        });

        function productReadySuper() {
            return productReady.then(function (productId) {
                $form.find(productSelector.join(', ')).val(productId);
                self.rootProduct = {
                    product_template_id: parseInt($form.find('.product_template_id').val()),
                    product_id: productId,
                    quantity: parseFloat($form.find('input[name="add_qty"]').val() || 1),
                    product_custom_attribute_values: self.getCustomVariantValues($form.find('.js_product')),
                    variant_values: self.getSelectedVariantValues($form.find('.js_product')),
                    no_variant_attribute_values: self.getNoVariantAttributeValues($form.find('.js_product')),
                    no_variant_attribute_values: self.getNoVariantAttributeValues($form.find('.js_product')),
                    custom_options: JSON.stringify(wk_custom_options)
                };
                return self._onProductReady();
            });
        }

        return new Promise((resolve, reject) => {
            function ajax_check() {
                if (file_load_check || no_file) {
                    file_load_check = false
                    clearInterval(check_ajax);
                    resolve(productReadySuper());
                }
            }
            var check_ajax = setInterval(ajax_check, 100);
        });
    },
});


