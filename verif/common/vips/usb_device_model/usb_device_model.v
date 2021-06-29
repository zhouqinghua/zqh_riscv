`timescale 1ns / 1ps

`define USB_DEV_ST_DISCON 0
`define USB_DEV_ST_CON 1
`define USB_DEV_ST_IDLE 2

//`define USB_DEV_CON_TICK 24000
`define USB_DEV_CON_TICK 30
module usb_device_model(
    input Vbus,
    inout Dp,
    inout Dm,
    input GND
);
    parameter MODE = 1;//0: low speed, 1: full/low speed, 2: high/full/low speed

    reg clk_ref;//384MHz
    initial begin
        clk_ref = 0;
        while(1) begin
            #1.302ns;
            clk_ref <= ~clk_ref;
        end
    end

    reg reset;
    always @(posedge clk_ref) begin
        if (Vbus === 1) begin
            reset <= 0;
        end
        else begin
            reset <= 1;
        end
    end

    reg[7:0] clk_div = 32;
    //tx clock
    reg[7:0] tx_clk_cnt;
    always @(posedge clk_ref or posedge reset) begin
        if (reset) begin
            tx_clk_cnt <= 0;
        end
        else begin
            if (tx_clk_cnt == (clk_div - 1)) begin
                tx_clk_cnt <= 0;
            end
            else begin
                tx_clk_cnt <= tx_clk_cnt + 1;
            end
        end
    end
    reg tx_clk;
    always @(posedge clk_ref or posedge reset) begin
        if (reset) begin
            tx_clk <= 0;
        end
        else begin
            if (tx_clk_cnt == 0) begin
                tx_clk <= 0;
            end
            else if (tx_clk_cnt == clk_div/2) begin
                tx_clk <= 1;
            end
        end
    end


    //rx clock
    reg dp_dly0,dp_dly1;
    wire dp_pos;
    wire dp_neg;
    always @(posedge clk_ref) begin
        dp_dly0 <= Dp;
        dp_dly1 <= dp_dly0;
    end
    assign dp_pos = dp_dly0 & ~dp_dly1;
    assign dp_neg = ~dp_dly0 & dp_dly1;

    reg[7:0] rx_clk_cnt;
    always @(posedge clk_ref or posedge reset) begin
        if (reset) begin
            rx_clk_cnt <= 0;
        end
        else begin
            if (rx_clk_cnt == (clk_div - 1)) begin
                rx_clk_cnt <= 0;
            end
            else if (dp_pos | dp_neg) begin
                rx_clk_cnt <= 0;
            end
            else begin
                rx_clk_cnt <= rx_clk_cnt + 1;
            end
        end
    end
    reg rx_clk;
    always @(posedge clk_ref or posedge reset) begin
        if (reset) begin
            rx_clk <= 0;
        end
        else begin
            if (rx_clk_cnt == 0) begin
                rx_clk <= 0;
            end
            else if (rx_clk_cnt == clk_div/2) begin
                rx_clk <= 1;
            end
        end
    end


    //usb tx
    reg dp_out_reg;
    reg dm_out_reg;
    reg[3:0] state;
    reg[31:0] cnt;
    always @(posedge tx_clk or posedge reset) begin
        if (reset) begin
            state <=  `USB_DEV_ST_DISCON;
        end
        else begin
            case(state)
                `USB_DEV_ST_DISCON : begin
                    state <= `USB_DEV_ST_CON;
                    cnt <= 0;
                end
                `USB_DEV_ST_CON : begin
                    if (cnt == `USB_DEV_CON_TICK) begin
                        state <= `USB_DEV_ST_IDLE;
                    end
                    else begin
                        cnt <= cnt + 1;
                    end
                end
                `USB_DEV_ST_IDLE : begin
                    state <= `USB_DEV_ST_IDLE;
                    cnt <= 0;
                end
                default : begin
                end
            endcase
        end
    end

    always @(posedge tx_clk or posedge reset) begin
        if (reset) begin
            dp_out_reg <= 0;
            dm_out_reg <= 0;
        end
        else begin
            if (state == `USB_DEV_ST_DISCON) begin
                dp_out_reg <= 0;
                dm_out_reg <= 0;
            end
            else if (state == `USB_DEV_ST_CON) begin
                dp_out_reg <= 1'bz;
                dm_out_reg <= 1'bz;
            end
            else if (state == `USB_DEV_ST_IDLE) begin
                dp_out_reg <= 1'bz;
                dm_out_reg <= 1'bz;
            end
        end
    end

    assign Dp = dp_out_reg;
    assign Dm = dm_out_reg;
    pullup(pull1) pu_dp (Dp);


    //usb rx
endmodule
