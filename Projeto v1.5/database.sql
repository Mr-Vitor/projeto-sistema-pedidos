CREATE DATABASE IF NOT EXISTS pedido_gestao;
USE pedido_gestao;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'usuario') DEFAULT 'usuario'
);

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(15),
    endereco TEXT
);

CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    estoque INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total DECIMAL(10,2),
    usuario_id INT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pedidos_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT,
    produto_id INT,
    quantidade INT NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS logs_pedidos (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    operacao ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    id_pedido INT NULL,
    id_cliente INT NOT NULL,
    usuario_id INT NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id) ON DELETE SET NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);	



DELIMITER //

CREATE FUNCTION calcular_valor_pedido(pedido_id INT) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    
    -- Calcula o valor total somando (quantidade * preço) de cada produto no pedido
    SELECT SUM(pp.quantidade * pr.preco)
    INTO total
    FROM pedidos_produtos pp
    JOIN produtos pr ON pp.produto_id = pr.id
    WHERE pp.pedido_id = pedido_id;

    -- Retorna 0 se o pedido não tiver produtos
    RETURN IFNULL(total, 0);
END //

DELIMITER ;


DELIMITER //

CREATE PROCEDURE validar_pedido(
    IN id_cliente INT,
    IN id_produto INT,
    IN quantidade INT,
    OUT resultado BOOLEAN
)
BEGIN
    DECLARE estoque_atual INT;
    
    -- Obtém o estoque disponível do produto
    SELECT estoque INTO estoque_atual
    FROM produtos
    WHERE id = id_produto;

    -- Verifica se o produto existe e se há estoque suficiente
    IF estoque_atual IS NULL THEN
        SET resultado = FALSE;
    ELSEIF estoque_atual >= quantidade THEN
        SET resultado = TRUE;
    ELSE
        SET resultado = FALSE;
    END IF;
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER atualizar_estoque
BEFORE UPDATE ON pedidos_produtos
FOR EACH ROW
BEGIN
    DECLARE diferenca INT;

    -- 🔹 Calcula a diferença de quantidades ANTES da atualização
    SET diferenca = NEW.quantidade - OLD.quantidade;

    -- 🔹 Se a nova quantidade for maior, reduz estoque | Se for menor, repõe estoque
    UPDATE produtos
    SET estoque = estoque - diferenca
    WHERE id = OLD.produto_id;
END //

DELIMITER ;


DELIMITER //
CREATE TRIGGER after_insert_pedido
AFTER INSERT ON pedidos
FOR EACH ROW
BEGIN
    INSERT INTO logs_pedidos (operacao, id_pedido, id_cliente, usuario_id)
    VALUES ('INSERT', NEW.id, NEW.cliente_id, NEW.usuario_id);
END;
//
DELIMITER ;


DELIMITER //
CREATE TRIGGER after_update_pedido
AFTER UPDATE ON pedidos
FOR EACH ROW
BEGIN
    INSERT INTO logs_pedidos (operacao, id_pedido, id_cliente, usuario_id)
    VALUES ('UPDATE', NEW.id, NEW.cliente_id, NEW.usuario_id);
END;
//
DELIMITER ;


DELIMITER //
CREATE TRIGGER before_delete_pedido
BEFORE DELETE ON pedidos
FOR EACH ROW
BEGIN
    INSERT INTO logs_pedidos (operacao, id_pedido, id_cliente, usuario_id, data_hora)
    VALUES ('DELETE', OLD.id, OLD.cliente_id, OLD.usuario_id, NOW());
END;
//
DELIMITER ;

