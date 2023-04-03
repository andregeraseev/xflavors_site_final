<!--avise-me-->

$(document).ready(function() {
  $(".avise-me-button").click(function() {
    let productId = $(this).data('product-id');
    console.log("Product ID: ", productId);
    var url = "{% url 'avise:aviso_estoque' %}";
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();

    // Encontra o botão "avise-me" correspondente no outro carrossel usando o mesmo "productId"
    var otherButton = $('#carousel-1 .avise-me-button[data-product-id="' + productId + '"]');
    if (otherButton.length == 0) {
      otherButton = $('#carousel-2 .avise-me-button[data-product-id="' + productId + '"]');
    }

    $.ajax({
      url: url,
      method: "POST",
      data: {
        product_id: productId,
        csrfmiddlewaretoken: csrftoken
      },
       success: function(data) {
        if (data.success) {
          // Exibe uma mensagem de sucesso
        $('#alert_success').show();
        $('#alert_container_success').show();
        $('#alert_success').html(data.aviso_adicionado);

        // Oculta a mensagem de sucesso após 5 segundos
        setTimeout(function() {
          $('#alert_success').hide();
          $('#alert_container_success').hide();
        }, 5000);


          // Muda o botão "avise-me" nos dois carrosséis para "Aguardando Restoque"
          var buttonHtml = "<button class='btn btn-warning btn-sm w-100' disabled id='botao_aguardando'>Aguardando Restoque</button>";
          $(".avise-me-button[data-product-id='" + productId + "']").replaceWith(buttonHtml);
          otherButton.replaceWith(buttonHtml);
        }
        else {
           // Exibe uma mensagem de erro
        $('#available-stock').text(data.mensagem);
        $('#alert-erro').show();
        $('#alert-container-erro').show();
        $('#alert-erro').html(data.mensagem);

        // Oculta a mensagem de erro após 5 segundos
        setTimeout(function() {
          $('#alert-erro').hide();
          $('#alert-container-erro').hide();
        }, 5000);

        }
      },
      error: function(xhr, errmsg, err) {
        alert("Erro ao cadastrar aviso!" + errmsg.message);
      }
    });
  });
});