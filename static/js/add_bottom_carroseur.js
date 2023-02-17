
  $(document).ready(function () {
    $('.add-to-cart-button').click(function () {
      let productId = $(this).data('product-id');
      let quantity = $(`.quantity-input[data-product-id=${productId}]`).val();


      $.ajax({
        type: 'POST',
        url: "{% url 'add_to_cart' %}",
        data: {
          'productId': productId,
          'quantity': quantity,
          'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        dataType: 'json',
        success: function (data) {
          if (data.success) {
                        $('#add_to_cart_alert').show();
                        $('#alert_container').show();
                        setTimeout(function() {
                            $('#add_to_cart_alert').hide();
                            $('#alert_container').hide();
                        }, 5000);
                    } else {
                     $('#available-stock').text(data.stock);
                     $('#alert-stock').show();
                     $('#alert-container-stock').show();
                     setTimeout(function() {
                            $('#alert-stock').hide();
                            $('#alert-container-stock').hide();
                        }, 5000);
                    }
                },
                error: function (data) {
                    alert('Ocorreu um erro ao adicionar o produto ao carrinho. Tente novamente mais tarde.');
                }
            });
        });
    });
