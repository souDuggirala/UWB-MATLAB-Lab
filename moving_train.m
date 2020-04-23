for i=0:1:360
        x1=(0.35*sin(i)+1.16);
        y1=(0.35*cos(i)+0.55);
        truevalue1 = plot(x1,y1,'+'); hold on
end
for i=0:1:360
        x1=(0.55*sin(i)+1.16);
        y1=(0.55*cos(i)+0.55);
        truevalue2 = plot(x1,y1,'+'); hold on
end
for i=0:1:360
        x1=(0.45*sin(i)+1.16);
        y1=(0.45*cos(i)+0.55);
        truevalue = plot(x1,y1,'.'); hold on
end
hold on
num1=xlsread('moving_train1.xlsx');
X=num1(:,1);
Y=num1(:,2);
ans1=plot(X,Y,'-')
xlim([0 10])
ylim([-0.4 0.8])
hold off
legend([ans1, truevalue, truevalue1, truevalue2], 'Decawave', 'True Value', 'True Value with Buffer', 'True Value with Buffer');
