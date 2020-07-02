function RealTimePlotWithSerialPort()
s=serialport("COM8",115200);
cleanup = onCleanup(@()myCleanup(s));
x_anch=[0,0,2.33,2.33];
y_anch=[0,1.11,1.11,0];
figure();
box on;
set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
plot(x_anch, y_anch, 'r^');
axis([-0.5 4 -0.5 1.5]);
daspect([1 1 1]);
grid on;
hold on;
while(1)
    data = readline(s);
    new = split(data,",");
    X=str2double(new(4));
    Y=str2double(new(5));
    check = geofencing(X,Y);
    if(check)
        disp("OUT OF ZONE")
    end
    plot(X,Y, 'b^');
    hold on
end

end



function check = geofencing(X,Y)
check = false;
if ((X < 0) || (Y < 0)|| (X > 2.33)|| (Y>1.11))
   check=true; 
end
end


function myCleanup(S)
disp('Port Close');
delete(S);
end
