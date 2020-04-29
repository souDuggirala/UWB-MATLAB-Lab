
%Buffer(-0.2 m)
centers=[1.16, 0.55];
<<<<<<< HEAD
radii=0.25;
buffer1=viscircles(centers,radii,'LineWidth',0.5,'LineStyle','--','Color','g');
=======
radii=0.35;
buffer1=viscircles(centers,radii, 'LineStyle', '--', 'LineWidth', 1);
>>>>>>> 28c94679a4f330c76c7df0ca61e83efed7a126e1
hold on

%Buffer(+0.2 m)
centers=[1.16, 0.55];
<<<<<<< HEAD
radii=0.65;
buffer2=viscircles(centers,radii,'LineWidth',0.5,'LineStyle','--','Color','g');
=======
radii=0.55;
buffer2=viscircles(centers,radii, 'LineStyle', '--', 'LineWidth', 1);
>>>>>>> 28c94679a4f330c76c7df0ca61e83efed7a126e1
hold on

%True Value
centers=[1.16, 0.55];
radii=0.45;
truevalue=viscircles(centers,radii,'LineWidth',0.5,'LineStyle','-','Color','r');
hold on

%Measured Value from decawave LOS
%num1=xlsread('moving_train1.xlsx');
%X_LOS=num1(:,1);
%Y_LOS=num1(:,2);
%ans1_LOS=plot(X_LOS,Y_LOS,'b-')

%Measured Value from decawave NLOS(Anchor 3 blocked)
<<<<<<< HEAD
num1=xlsread('NLOS_movingtrain_1anchor.xlsx');
X_NLOS=num1(:,1);
Y_NLOS=num1(:,2);
ans1_NLOS=plot(X_NLOS,Y_NLOS,'b-')
=======
%num1=xlsread('NLOS_movingtrain_1anchor.xlsx');
%X_NLOS=num1(:,1);
%Y_NLOS=num1(:,2);
%ans1_NLOS=plot(X_NLOS,Y_NLOS,'b-', 'edgealpha',0.2)
>>>>>>> 28c94679a4f330c76c7df0ca61e83efed7a126e1


%axis([0 3 0 3]);

%Anchor Positions
x_anch=[0, 0, 2.33, 2.33]
y_anch=[0,1.11,1.11,0];
anch=plot(x_anch,y_anch,'b^');

xlim([-.5,3.5]);
ylim([-.5,1.5]);
daspect([1 1 1])
grid on
hold off


legend([ans1_NLOS, truevalue, buffer1, buffer2,anch], 'Measured value', 'True Value', 'Buffer(-0.2m)', 'Buffer(+0.2m)','Anchor');
title('Moving train');
xlabel('Distance in meters');
ylabel('Distance in meters');

