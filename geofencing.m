x=[0,0.25,0.5,0.75,1,1.25,1.5,1.75];%Ground truth
y=[1.4,1.4,1.4,1.4,1.4,1.4,1.4,1.4,];
ans1=plot(x,y,'-');
hold on

x_geo1=[-0.033,0.280,0.297,0.778,1.093,1.367,1.64,1.95];%5 anchors data Slide 18
y_geo1=[1.344,1.412,1.416,1.552,1.491,1.576,1.59,1.56];

x_geo2=[0.061,0.432,0.653,0.946,1.064,1.296,1.656,1.75];%6 anchors slide data slide 20
y_geo2=[1.47,1.47,1.41,1.434,1.418,1.490,1.510,1.513];

ans2=plot(x_geo1,y_geo1,'-');
ans3=plot(x_geo2,y_geo2,'-');
axis([0 2 0 2.8]);
legend([ans1,ans2,ans3],'True value','Measured value with 5 anchors','Measured value with 6 anchors');
title('Geofencing');

