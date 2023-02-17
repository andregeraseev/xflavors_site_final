$(document).ready(function() {

  // Seleciona o elemento HTML com ID "variation"
  let variationSelect = $('#variation');


  // Função para atualizar a variação selecionada
  function updateSelectedVariation() {
    // Obtém o ID da variação selecionada, ou o ID da primeira variação se nenhuma for selecionada
    let selectedVariationId = variationSelect.val() || variationSelect.find('option:first').val();
    // Obtém o preço da variação selecionada
    let selectedVariationPrice = variationSelect.find('option:selected').text().split(' - R$ ')[1];

    console.log('selectedVariationId:', selectedVariationId);
  console.log('selectedVariationPrice:', selectedVariationPrice);
    // Atualiza o preço exibido
    $('#price').text('R$ ' + selectedVariationPrice);
    // Define o ID da variação selecionada no botão "Adicionar ao carrinho"
    $('.add-to-cart-button').data('variation-id', selectedVariationId);
  }

  // Associa a função "updateSelectedVariation" ao evento "change" do select de variações
  variationSelect.change(updateSelectedVariation);
  // Chama a função "updateSelectedVariation" para exibir a variação selecionada inicialmente
  updateSelectedVariation();

  // Associa a função abaixo ao evento "click" do botão "Adicionar ao carrinho"
  $('.add-to-cart-button').click(function() {
    let productId = $(this).data('product-id');
    let variationId = $(this).data('variation-id');
    let quantity = $(this).siblings('.quantity-input').val();

    console.log('productId:', productId);
  console.log('variationId:', variationId);
  console.log('quantity:', quantity);


    // Envia uma requisição AJAX para adicionar o produto ao carrinho
    $.ajax({
      type: 'POST',
      url: '{% url "add_to_cart_carrocel" %}',
      data: {
        'productId': productId,
        'variation_id': variationId,
        'quantity': quantity,
        'csrfmiddlewaretoken': '{{ csrf_token }}'
      },
      dataType: 'json',
      success: function(data) {
        if (data.success) {
          // Recarrega o ícone do carrinho
          $('#cart-icon').load(document.URL + ' #cart-icon');

          // Exibe uma mensagem de sucesso
          $('#alert_success').show();
          $('#alert_container_success').show();
          $('#alert_success').html(data.produto_adicionado);

          // Oculta a mensagem de sucesso após 5 segundos
          setTimeout(function() {
            $('#alert_success').hide();
            $('#alert_container_success').hide();
          }, 5000);

          // Define o valor do input de quantidade para 1
          $('.quantity-input[data-product-id=' + productId + ']').val(1);
        } else {
          // Exibe uma mensagem de erro
          $('#available-stock').text(data.stock);
          $('#alert-erro').show();
          $('#alert-container-erro').show();
          $('#alert-erro').html(data.error);

          // Oculta a mensagem de erro após 5 segundos
          setTimeout(function() {
            $('#alert-erro').hide();
            $('#alert-container-erro').hide();
          }, 5000);

          // Define o valor do input de quantidade para 1
          $('.quantity-input[data-product-id=' + productId + ']').val(1);
        }
      },
      error: function(data) {
        alert('Ocorreu um erro ao adicionar o produto ao carrinho. Tente novamente mais tarde.');
      }
    });
  });

  // Seleciona o elemento com a classe 'slick-list' e aplica o plugin slick()
let slickList = $('.slick-list');
slickList.slick({
  slidesToShow: 4,
  slidesToScroll: 1,
  arrows: true,
  infinite: true,
  autoplay: false,
  // Define a configuração do número de slides exibidos em diferentes tamanhos de tela
  responsive: [
    {
      breakpoint: 992,
      settings: {
        slidesToShow: 3
      }
    },
    {
      breakpoint: 576,
      settings: {
        slidesToShow: 1
      }
    }
  ]
});

// Seleciona os elementos com a classe 'prev-btn' e 'next-btn' e adiciona um listener para as ações de clique, que chama os métodos do plugin slick()
let prevBtn = $('.prev-btn');
let nextBtn = $('.next-btn');

prevBtn.click(function() {
  slickList.slick('slickPrev');
});

nextBtn.click(function() {
  slickList.slick('slickNext');
});

// Adiciona um listener para o evento 'afterChange' do plugin slick() que define a classe 'slick-disabled' nos botões 'prev-btn' e 'next-btn' com base na posição do slide atual
slickList.on('afterChange', function(event, slick, currentSlide) {
  prevBtn.toggleClass('slick-disabled', currentSlide === 0);
  nextBtn.toggleClass('slick-disabled', currentSlide === slick.slideCount - 1);
});
});

</script>