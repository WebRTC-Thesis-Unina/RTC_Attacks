const { EC2Client, StartInstancesCommand, StopInstancesCommand, DescribeInstancesCommand } = require("@aws-sdk/client-ec2");
require('dotenv').config(); 

const region = process.env.AWS_REGION

const client = new EC2Client({
    region: region,
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    }
})
const instanceId = process.env.INSTANCE_ID;

async function startInstance() {
    await client.send(new StartInstancesCommand({ InstanceIds: [instanceId] }));

    await new Promise(resolve => setTimeout(resolve, 5000));

    const desc = await client.send(new DescribeInstancesCommand({ InstanceIds: [instanceId] }));
    const instance = desc.Reservations[0].Instances[0];
    
    const privateIp = instance.PrivateIpAddress;
    const publicIp = instance.PublicIpAddress;

    return {privateIp, publicIp, region};
}

async function stopInstance() {

    await client.send(new StopInstancesCommand({ InstanceIds: [instanceId] }));

    const desc = await client.send(new DescribeInstancesCommand({ InstanceIds: [instanceId] }));
    const instance = desc.Reservations[0].Instances[0];
    const privateIp = instance.PrivateIpAddress;
    const publicIp = instance.PublicIpAddress;

    return {privateIp, publicIp};
}

module.exports = { startInstance, stopInstance };