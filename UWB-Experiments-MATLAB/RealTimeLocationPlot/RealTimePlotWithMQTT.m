function RealTimePlotWithMQTT()
M = mqtt('tcp://172.16.46.92');
cleanup = onCleanup(@()myCleanup(M));
x_anch=[0,0,2.33,2.33];
y_anch=[0,1.11,1.11,0];
figure();
box on;
set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
plot(x_anch, y_anch, 'r^');
axis([-0.5 10 -0.5 2.5]);
daspect([1 1 1]);
grid on;
hold on;
while (1)
    M = mqtt('tcp://172.16.46.92');
    mysub = subscribe(M,'dwm/node/47a3/uplink/location');
    pause(0.8);
    if(mysub.MessageCount==0)
        disp("No Message to read");
    else
        msg = read(mysub);
        position = jsondecode(msg);
        check = geofencing(position.position.x,position.position.y);
        if(check)
            disp("OUT OF ZONE")
        end
        plot(position.position.x,position.position.y, 'b^');
        hold on
    end

end

end



function check = geofencing(X,Y)
check = false;
if ((X < 0) || (Y < 0)|| (X > 6.33)|| (Y>6.33))
   check=true; 
end
end


function myCleanup(M)
disp('Close MQTT');
delete(M);
end

