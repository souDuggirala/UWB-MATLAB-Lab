x=[0,0.25,0.5,0.75,1,1.25,1.5,1.75];%Ground truth
y=[1.4,1.4,1.4,1.4,1.4,1.4,1.4,1.4,];
ans1=plot(x,y,'*');
hold on

%Anchor position for geo_1
%anchor1=plot(0,0,'^');
%anchor2=plot(1,0,'^');
%anchor3=plot(2,0,'^');
%anchor4=plot(0,2.8,'^');
%anchor5=plot(2,2.8,'^');

%Anchor position for geo_2
anchor1=plot(0,0,'^');
anchor2=plot(1,0,'^');
anchor3=plot(2,0,'^');
anchor4=plot(0,2.8,'^');
anchor5=plot(2,2.8,'^');
anchor6=plot(1,0.7,'^');
%Plot the buffer (+-10cm) for decawave
rectangle('Position',[-0.10 1.3 2 0.25]);

x_geo1=[-0.033,0.280,0.297,0.778,1.093,1.367,1.64,1.95];%5 anchors data Slide 18
y_geo1=[1.344,1.412,1.416,1.552,1.491,1.576,1.59,1.56];
x_geo1_std=[0.087,0.038,0.038,0.030,0.026,0.018,0.025,0.029];
y_geo1_std=[0.028,0.017,0.017,0.021,0.015,0.010,0.014,0.013];

x_geo2=[0.061,0.432,0.653,0.946,1.064,1.296,1.656,1.75];%6 anchors slide data slide 20
y_geo2=[1.47,1.47,1.41,1.434,1.418,1.490,1.510,1.513];
x_geo2_std=[0.028,0.041,0.047,0.036,0.019,0.037,0.028,0.025];
y_geo2_std=[0.015,0.021,0.028,0.026,0.013,0.014,0.013,0.012];

%Plot the std. Deviation for all data points
for i = 1:1:8
    theta = 0 : 0.01 : 2*pi;
    xcenter=x_geo2(i);
    ycenter=y_geo2(i);
    xradius=x_geo2_std(i);
    yradius=y_geo2_std(i);
    x_s = xradius * cos(theta) + xcenter;
    y_s = yradius * sin(theta) + ycenter;
    
   h = fill(x_s,y_s,'b');
% Choose a number between 0 (invisible) and 1 (opaque) for facealpha.  
    set(h,'facealpha',.7)
   a5=plot(x_s, y_s);
    hold on
end


ans2=plot(x_geo2,y_geo2,'o');
%ans3=plot(x_geo2,y_geo2,'o');
axis([-0.5 3 -0.5 3]);
legend([ans1,ans2,a5,anchor1,anchor2,anchor3,anchor4,anchor5,anchor6],'True value','Measured value','Standard Deviation','anchor1','anchor2','anchor3','anchor4','anchor5','anchor6');
title('Geofencing');
xlabel('Distance in meters');
ylabel('Distance in meters');



