cat > templates/pedidos.html << 'EOF'
{% extends "base.html" %}

{% block title %}Pedidos - Tienda FUNCA{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4"><i class="fas fa-clipboard-list"></i> Gestión de Pedidos</h1>
    </div>
</div>

<ul class="nav nav-tabs mb-4">
    <li class="nav-item">
        <a class="nav-link active" data-bs-toggle="tab" href="#pendientes">Pendientes de Recibir</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#entregar">Pendientes de Entregar al Cliente</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#completados">Completados</a>
    </li>
</ul>

<div class="tab-content">
    <!-- Pestaña: Pendientes de Recibir del Proveedor -->
    <div class="tab-pane fade show active" id="pendientes">
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>Pedido</th><th>Factura</th><th>Cliente</th><th>Proveedor</th><th>Producto</th><th>Solicitado</th><th>Recibido</th><th>Pendiente</th><th>Acciones</th></tr>
                        </thead>
                        <tbody id="tabla-pedidos-pendientes-recibir"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Pestaña: Pendientes de Entregar al Cliente -->
    <div class="tab-pane fade" id="entregar">
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr><th>Factura</th><th>Cliente</th><th>Producto</th><th>Recibido</th><th>Entregado</th><th>Pendiente</th><th>Acciones</th></tr>
                        </thead>
                        <tbody id="tabla-pedidos-pendientes-entregar"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Pestaña: Completados -->
    <div class="tab-pane fade" id="completados">
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead><tr><th>Factura</th><th>Cliente</th><th>Producto</th><th>Cantidad</th><th>Fecha Entrega</th></tr></thead>
                        <tbody id="tabla-pedidos-completados"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal para recibir pedido -->
<div class="modal fade" id="modalRecibirPedido" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-success text-white">
                <h5 class="modal-title">Recibir Productos del Proveedor</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="recibirInfo"></div>
                <div class="mb-3">
                    <label class="form-label">Cantidad a Recibir</label>
                    <input type="number" id="recibirCantidad" class="form-control" min="1">
                </div>
                <div class="mb-3">
                    <label class="form-label">Observaciones</label>
                    <textarea id="recibirObservaciones" class="form-control" rows="2"></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-success" onclick="confirmarRecepcion()">Confirmar Recepción</button>
            </div>
        </div>
    </div>
</div>

<!-- Modal para entregar al cliente -->
<div class="modal fade" id="modalEntregarCliente" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-warning text-white">
                <h5 class="modal-title">Entregar Producto al Cliente</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="entregarInfo"></div>
                <div class="mb-3">
                    <label class="form-label">Cantidad a Entregar</label>
                    <input type="number" id="entregarCantidad" class="form-control" min="1">
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-warning" onclick="confirmarEntrega()">Confirmar Entrega</button>
            </div>
        </div>
    </div>
</div>

<script>
let pedidoActual = null;

function cargarPedidos() {
    fetch('/api/pedidos-venta/detallados')
        .then(response => response.json())
        .then(data => {
            // Pendientes de recibir
            let pendientesRecibir = data.filter(p => p.cantidad_recibida < p.cantidad_solicitada);
            let recibirHtml = '';
            pendientesRecibir.forEach(p => {
                recibirHtml += `<tr>
                    <td>${p.numero_pedido}</td>
                    <td><a href="/factura?id=${p.venta_id}" target="_blank">${p.numero_factura}</a></td>
                    <td>${p.cliente}</td>
                    <td>${p.proveedor}</td>
                    <td>${p.producto_nombre}</td>
                    <td>${p.cantidad_solicitada}</td>
                    <td>${p.cantidad_recibida}</td>
                    <td>${p.cantidad_solicitada - p.cantidad_recibida}</td>
                    <td><button class="btn btn-sm btn-success" onclick="abrirRecibir(${p.pedido_detalle_id}, '${p.producto_nombre}', ${p.cantidad_solicitada - p.cantidad_recibida})">Recibir</button></td>
                </tr>`;
            });
            document.getElementById('tabla-pedidos-pendientes-recibir').innerHTML = recibirHtml || '<tr><td colspan="9">No hay pedidos pendientes</td></tr>';
            
            // Pendientes de entregar al cliente
            let pendientesEntregar = data.filter(p => p.cantidad_recibida > 0 && (p.entregado_cliente || 0) < p.cantidad_recibida);
            let entregarHtml = '';
            pendientesEntregar.forEach(p => {
                let pendiente = p.cantidad_recibida - (p.entregado_cliente || 0);
                entregarHtml += `<tr>
                    <td><a href="/factura?id=${p.venta_id}" target="_blank">${p.numero_factura}</a></td>
                    <td>${p.cliente}</td>
                    <td>${p.producto_nombre}</td>
                    <td>${p.cantidad_recibida}</td>
                    <td>${p.entregado_cliente || 0}</td>
                    <td>${pendiente}</td>
                    <td><button class="btn btn-sm btn-warning" onclick="abrirEntregar(${p.venta_id}, ${p.producto_id}, '${p.producto_nombre}', ${pendiente})">Entregar</button></td>
                </tr>`;
            });
            document.getElementById('tabla-pedidos-pendientes-entregar').innerHTML = entregarHtml || '<tr><td colspan="7">No hay productos pendientes de entregar</td></tr>';
            
            // Completados
            let completados = data.filter(p => (p.entregado_cliente || 0) >= p.cantidad_recibida && p.cantidad_recibida > 0);
            let completadosHtml = '';
            completados.forEach(p => {
                completadosHtml += `<tr>
                    <td><a href="/factura?id=${p.venta_id}" target="_blank">${p.numero_factura}</a></td>
                    <td>${p.cliente}</td>
                    <td>${p.producto_nombre}</td>
                    <td>${p.cantidad_recibida}</td>
                    <td>${new Date(p.fecha_entrega_cliente).toLocaleDateString() || '-'}</td>
                </tr>`;
            });
            document.getElementById('tabla-pedidos-completados').innerHTML = completadosHtml || '<tr><td colspan="5">No hay pedidos completados</td></tr>';
        });
}

function abrirRecibir(pedidoDetalleId, productoNombre, maxCantidad) {
    pedidoActual = { id: pedidoDetalleId, productoNombre: productoNombre, max: maxCantidad };
    document.getElementById('recibirInfo').innerHTML = `<p><strong>Producto:</strong> ${productoNombre}<br><strong>Pendiente por recibir:</strong> ${maxCantidad}</p>`;
    document.getElementById('recibirCantidad').value = maxCantidad;
    document.getElementById('recibirCantidad').max = maxCantidad;
    new bootstrap.Modal(document.getElementById('modalRecibirPedido')).show();
}

function confirmarRecepcion() {
    let cantidad = parseInt(document.getElementById('recibirCantidad').value);
    if (cantidad < 1 || cantidad > pedidoActual.max) {
        mostrarAlerta('Cantidad inválida', 'warning');
        return;
    }
    
    fetch('/api/pedidos-detalle/recibir', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            pedido_detalle_id: pedidoActual.id,
            cantidad: cantidad,
            observaciones: document.getElementById('recibirObservaciones').value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            mostrarAlerta(data.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalRecibirPedido')).hide();
            cargarPedidos();
        } else {
            mostrarAlerta(data.error, 'danger');
        }
    });
}

function abrirEntregar(ventaId, productoId, productoNombre, pendiente) {
    pedidoActual = { ventaId: ventaId, productoId: productoId, productoNombre: productoNombre, max: pendiente };
    document.getElementById('entregarInfo').innerHTML = `<p><strong>Producto:</strong> ${productoNombre}<br><strong>Pendiente por entregar:</strong> ${pendiente}</p>`;
    document.getElementById('entregarCantidad').value = pendiente;
    document.getElementById('entregarCantidad').max = pendiente;
    new bootstrap.Modal(document.getElementById('modalEntregarCliente')).show();
}

function confirmarEntrega() {
    let cantidad = parseInt(document.getElementById('entregarCantidad').value);
    if (cantidad < 1 || cantidad > pedidoActual.max) {
        mostrarAlerta('Cantidad inválida', 'warning');
        return;
    }
    
    fetch(`/api/ventas/${pedidoActual.ventaId}/entregar-producto`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            producto_id: pedidoActual.productoId,
            cantidad: cantidad
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            mostrarAlerta(data.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('modalEntregarCliente')).hide();
            cargarPedidos();
        } else {
            mostrarAlerta(data.error, 'danger');
        }
    });
}

document.addEventListener('DOMContentLoaded', cargarPedidos);
</script>
{% endblock %}
EOF
