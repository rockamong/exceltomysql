CREATE DATABASE IF NOT EXISTS EntPrice CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE EntPrice;

CREATE TABLE IF NOT EXISTS price (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shebei_mingcheng VARCHAR(255) NOT NULL COMMENT '设备名称',
    shebei_canshu TEXT COMMENT '设备参数',
    shebei_danjia DECIMAL(10, 2) NOT NULL COMMENT '设备单价',
    luru_shijian TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '录入时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
