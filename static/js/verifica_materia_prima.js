<!--INICIO-->
var materiaPrimaIds = [];
var quantidadeTotalDesejada = 0;
var estoqueInsuficiente = false;

{% for item in itens %}
  {% if item.variation %}
    var quantidadeDesejada{{ item.id }} = {{ item.quantity }}*{{ item.variation.gasto }};
    quantidadeTotalDesejada += quantidadeDesejada{{ item.id }};
    materiaPrimaIds.push({{ item.variation.materia_prima.id }});
  {% else %}
    var quantidadeDesejada{{ item.id }} = {{ item.quantity }};
    quantidadeTotalDesejada += quantidadeDesejada{{ item.id }};
    materiaPrimaIds.push({{ item.product.materia_prima.id }});
  {% endif %}
{% endfor %}

var materiaPrimaQuantidades = {};

// Loop para contar as quantidades totais de cada matéria prima necessária
for (var i = 0; i < materiaPrimaIds.length; i++) {
  var nomeMateriaPrima = '';
  var id = materiaPrimaIds[i];
  {% for item in itens %}
    {% if item.variation and item.variation.materia_prima.id == id %}
      nomeMateriaPrima = '{{ item.variation.materia_prima.name }}';
    {% elif item.product.materia_prima.id == id %}
      nomeMateriaPrima = '{{ item.product.materia_prima.name }}';
    {% endif %}
  {% endfor %}
  if (materiaPrimaQuantidades[id]) {
    materiaPrimaQuantidades[id] += quantidadeTotalDesejada;
  } else {
    materiaPrimaQuantidades[id] = quantidadeTotalDesejada;
  }
}

// Loop para verificar se há estoque suficiente para cada matéria prima
{% for item in itens %}
  {% if item.variation %}
    var quantidadeMateriaPrima{{ item.id }} = parseFloat('{{ item.variation.materia_prima.stock }}');
  {% else %}
    var quantidadeMateriaPrima{{ item.id }} = parseFloat('{{ item.product.materia_prima.stock }}');
  {% endif %}
{% endfor %}

for (var id in materiaPrimaQuantidades) {
  var quantidadeMateriaPrima = 0;
  {% for item in itens %}
    {% if item.variation and item.variation.materia_prima.id == id %}
      quantidadeMateriaPrima = quantidadeMateriaPrima{{ item.id }};
    {% elif item.product.materia_prima.id == id %}
      quantidadeMateriaPrima = quantidadeMateriaPrima{{ item.id }};
    {% endif %}
  {% endfor %}
  console.log('quantidadeMateriaPrima', quantidadeMateriaPrima);
  if (materiaPrimaQuantidades[id] > quantidadeMateriaPrima) {
    var alertContainer = $('#alert-container-erro');
    $('#alert-container-erro').show();
    alertContainer.show();
    $('#alert-erro').html('Estoque insuficiente para a matéria prima ' + nomeMateriaPrima + '. Temos apenas ' + quantidadeMateriaPrima + ' em estoque.');
    $('html, body').animate({
        scrollTop: alertContainer.offset().top
    }, 1000);
    estoqueInsuficiente = true;
    break;
  }
}

if (estoqueInsuficiente == true) {
  return false;
}

<!--FIMMMMMM-->